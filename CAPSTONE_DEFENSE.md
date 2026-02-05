# ErrandExpress Capstone Defense - Comprehensive Technical Documentation

## Executive Summary
ErrandExpress is a secure task marketplace platform that implements intelligent task prioritization, dynamic assignment, secure payment processing, and comprehensive monitoring systems. This document provides detailed proof of implementation for capstone defense.

---

# PART 1: CORE OBJECTIVES - TECHNICAL PROOF

## OBJECTIVE 1: Errand Prioritization & Scheduling System

### 📋 What It Does
Automatically ranks tasks based on 7 weighted factors: urgency, location, customer preferences, time windows, price, user ratings, and deadlines.

### 🔬 HOW & WHY IT WORKS

#### Implementation Architecture
**File:** `core/services.py` (Lines 13-280)  
**Class:** `PrioritizationService`

#### The Mathematical Formula
```python
priority_score = (urgency_factor × 1.5) + 
                 (location_factor × 2.0) + 
                 (preference_factor × 2.0) + 
                 (time_window_factor × 1.5) + 
                 (price_factor × 1.0) + 
                 (rating_factor × 2.0) + 
                 (deadline_factor × 1.0)
```

**Maximum Possible Score:** 11.0 points

#### Factor 1: Urgency Score
**File:** `core/services.py` (Lines 35-48)

```python
def calculate_urgency_score(priority_level):
    return Case(
        When(priority_level=5, then=Value(Decimal('1.50'))),  # Urgent
        When(priority_level=4, then=Value(Decimal('1.20'))),  # High
        When(priority_level=3, then=Value(Decimal('0.90'))),  # Normal
        When(priority_level=2, then=Value(Decimal('0.60'))),  # Low
        When(priority_level=1, then=Value(Decimal('0.30'))),  # Very Low
        default=Value(Decimal('0.90')),
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
```

**WHY:** Uses Django's `Case/When` for database-level computation (faster than Python loops). The priority_level field is set by task posters (1-5 scale) and directly influences ranking.

#### Factor 2: Location Match
**File:** `core/services.py` (Lines 50-61)

```python
def calculate_location_score(user_campus):
    return Case(
        When(campus_location=user_campus, then=Value(Decimal('2.00'))),
        When(campus_location='', then=Value(Decimal('0.50'))),
        default=Value(Decimal('0.00')),
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
```

**WHY:** Weight of 2.0 makes location the HIGHEST priority factor. Tasks in the same campus bubble to the top. This reduces travel time and increases task completion rates.

#### Factor 3: Customer Preferences
**File:** `core/models.py` (Lines 200-207)

```python
class Task(models.Model):
    preferred_doer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_tasks',
        help_text="Preferred doer for this task"
    )
```

**Scoring Logic:** `core/services.py` (Lines 63-73)
```python
def calculate_preference_score(user_id):
    return Case(
        When(preferred_doer_id=user_id, then=Value(Decimal('2.00'))),
        default=Value(Decimal('0.00')),
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
```

**WHY:** If a poster sets a "preferred doer," that specific user gets a +2.0 bonus, ensuring they see the task first. This enables repeat business relationships.

#### Factor 4: Time Windows
**File:** `core/models.py` (Lines 178-197)

```python
# Time Windows & Scheduling
time_window_start = models.DateTimeField(
    null=True, blank=True,
    help_text="Preferred start time for task execution"
)
time_window_end = models.DateTimeField(
    null=True, blank=True,
    help_text="Preferred end time for task execution"
)
flexible_timing = models.BooleanField(
    default=False,
    help_text="Allow flexible scheduling outside preferred window"
)
```

**Scoring Logic:** `core/services.py` (Lines 75-107)
```python
def calculate_time_window_score():
    now = timezone.now()
    return Case(
        # Task needs to be done RIGHT NOW (within time window)
        When(
            time_window_start__lte=now,
            time_window_end__gte=now,
            then=Value(Decimal('1.50'))  # HIGHEST score
        ),
        # Task is scheduled for TODAY
        When(
            time_window_start__date=now.date(),
            then=Value(Decimal('1.00'))
        ),
        # Flexible timing
        When(
            flexible_timing=True,
            then=Value(Decimal('0.50'))
        ),
        default=Value(Decimal('0.00')),
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
```

**WHY:** Tasks with active time windows (happening NOW) get maximum urgency. This ensures time-sensitive tasks don't get buried.

#### Factor 5: Deadline Urgency
**File:** `core/services.py` (Lines 129-150)

```python
def calculate_deadline_urgency_score():
    now = timezone.now()
    one_day = now + timedelta(days=1)
    three_days = now + timedelta(days=3)
    one_week = now + timedelta(days=7)
    
    return Case(
        When(deadline__lte=one_day, then=Value(Decimal('1.00'))),     # Due in 24h
        When(deadline__lte=three_days, then=Value(Decimal('0.70'))),  # Due in 3 days
        When(deadline__lte=one_week, then=Value(Decimal('0.40'))),    # Due in 1 week
        default=Value(Decimal('0.20')),                               # Due later
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
```

**WHY:** Creates a sliding scale of urgency. Tasks due in 24 hours get maximum deadline score.

#### Factor 6: Poster Rating
**File:** `core/services.py` (Lines 167-193)

```python
# Calculate REAL-TIME rating from Rating table
poster_rating_subquery = Rating.objects.filter(
    rated=OuterRef('poster')
).values('rated').annotate(
    avg_rating=Avg('score')
).values('avg_rating')

poster_rating_value = Coalesce(
    Subquery(poster_rating_subquery, output_field=DecimalField()),
    Value(Decimal('3.00'), output_field=DecimalField()),
    output_field=DecimalField(max_digits=4, decimal_places=2)
)

rating_factor = ExpressionWrapper(
    (F('poster_rating_value') / Value(Decimal('5.00'))) * RATING_WEIGHT,
    output_field=DecimalField(max_digits=5, decimal_places=2)
)
```

**WHY:** 
- Uses `Subquery` to calculate LIVE average ratings (not stale cached values)
- Normalizes 1-10 rating to 0.0-1.0 scale, then multiplies by weight (2.0)
- High-rated posters attract more doers (trustworthy clients get priority visibility)

#### Factor 7: Price Agreement
**File:** `core/services.py` (Lines 109-127)

```python
def calculate_price_score():
    return ExpressionWrapper(
        Case(
            When(price__gte=1000, then=Value(Decimal('1.00'))),           # Premium
            When(price__gte=500, then=F('price') / Value(Decimal('1000.0'))),  # High
            When(price__gte=100, then=F('price') / Value(Decimal('2000.0'))),  # Medium
            default=F('price') / Value(Decimal('5000.0')),                # Low
            output_field=DecimalField(max_digits=5, decimal_places=2)
        ),
        output_field=DecimalField(max_digits=5, decimal_places=2)
    )
```

**WHY:** Normalizes price to 0.0-1.0 scale. Higher-paying tasks get better visibility (incentivizes quality work).

### 📊 Database-Level Computation
**File:** `core/services.py` (Lines 175-206)

```python
prioritized_tasks = tasks_queryset.annotate(
    urgency_factor=cls.calculate_urgency_score(F('priority_level')),
    location_factor=cls.calculate_location_score(user.campus_location),
    preference_factor=cls.calculate_preference_score(user.id),
    time_window_factor=cls.calculate_time_window_score(),
    price_factor=cls.calculate_price_score(),
    deadline_factor=cls.calculate_deadline_urgency_score(),
    poster_rating_value=Coalesce(...),
    rating_factor=ExpressionWrapper(...),
    
    # FINAL SCORE CALCULATION
    priority_score=ExpressionWrapper(
        (F('urgency_factor') * cls.URGENCY_WEIGHT) +
        (F('location_factor') * cls.LOCATION_WEIGHT) +
        (F('preference_factor') * cls.PREFERENCE_WEIGHT) +
        (F('time_window_factor') * cls.TIME_WINDOW_WEIGHT) +
        (F('price_factor') * cls.PRICE_WEIGHT) +
        F('rating_factor') +
        (F('deadline_factor') * cls.DEADLINE_WEIGHT),
        output_field=DecimalField(max_digits=7, decimal_places=2)
    )
).order_by('-priority_score', '-price', '-created_at')
```

**WHY THIS IS EFFICIENT:**
- **No N+1 Queries:** All computations happen in a single SQL query
- **Database-Level Math:** PostgreSQL does the heavy lifting, not Python
- **Indexed Fields:** Uses `models.Index` on `priority_level`, `campus_location`, `deadline` for fast lookups

### 🗓️ Scheduling & Conflict Detection
**File:** `core/api_views.py` (Lines 225-314)

```python
@login_required
def api_get_scheduled_tasks(request):
    # Get user's tasks with time windows
    tasks = tasks.filter(
        time_window_start__isnull=False
    ).order_by('time_window_start')
    
    # Detect overlapping time windows
    conflicts = []
    for i, task1 in enumerate(tasks_list):
        for task2 in tasks_list[i+1:]:
            if (task1.time_window_start <= task2.time_window_end and
                task1.time_window_end >= task2.time_window_start):
                conflicts.append({
                    'task1_id': str(task1.id),
                    'task2_id': str(task2.id),
                    'overlap_start': max(...).isoformat(),
                    'overlap_end': min(...).isoformat()
                })
```

**WHY:** Prevents double-booking. If two tasks have overlapping time windows, the system warns the user.

---

## OBJECTIVE 2: Dynamic Task Assignment System

### 📋 What It Does
Automatically assigns tasks to the best-matching available agent based on skills, availability, location, rating, and workload.

### 🔬 HOW & WHY IT WORKS

#### Assignment Algorithm
**File:** `core/views.py` (Lines 252-326)

```python
def auto_assign_task(task, criteria=None):
    # STEP 1: Filter by skill requirements
    if task.category in ['typing', 'powerpoint', 'graphics']:
        skilled_agents = StudentSkill.objects.filter(
            status='verified',
            skill_name=task.category
        ).values_list('student_id', flat=True)
        available_agents = available_agents.filter(id__in=skilled_agents)
    else:
        # Microtasks: everyone qualifies
        available_agents = available_agents.filter(
            doer_type__in=['microtasker', 'both']
        )
    
    # STEP 2: Score each agent
    best_agent = None
    best_score = -1
    
    for agent in available_agents:
        scores = calculate_assignment_score(task, agent)
        if scores['total'] > best_score:
            best_score = scores['total']
            best_agent = agent
    
    # STEP 3: Create TaskAssignment record
    assignment = TaskAssignment.objects.create(
        task=task,
        agent=best_agent,
        assignment_method='automatic',
        total_match_score=best_score
    )
```

#### Scoring Function
**File:** `core/views.py` (Lines 143-205)

```python
def calculate_assignment_score(task, agent):
    # 1. SKILL MATCH (35% weight)
    if task.category in ['typing', 'powerpoint', 'graphics']:
        has_skill = StudentSkill.objects.filter(
            student=agent,
            skill_name=task.category,
            status='verified'
        ).exists()
        skill_match = 100 if has_skill else 0
    else:
        skill_match = 100  # Microtasks: everyone matches
    
    # 2. AVAILABILITY (20% weight)
    active_assignments = TaskAssignment.objects.filter(
        agent=agent,
        status__in=['assigned', 'in_progress']
    ).count()
    availability = 100 if active_assignments == 0 else 0
    
    # 3. LOCATION MATCH (20% weight)
    location_match = 100 if (task.campus_location and 
                             task.campus_location == agent.campus_location) else 0
    
    # 4. RATING (15% weight)
    rating = float(agent.avg_rating) * 20  # Normalize 0-5 to 0-100
    
    # 5. WORKLOAD BALANCE (10% weight)
    workload_score = max(0, 100 - (active_assignments * 10))
    
    # WEIGHTED TOTAL
    total_score = (
        (skill_match * 0.35) +
        (location_match * 0.20) +
        (availability * 0.20) +
        (rating * 0.15) +
        (workload_score * 0.10)
    )
    
    return {
        'skill_match': skill_match,
        'location_match': location_match,
        'availability': availability,
        'rating': rating,
        'workload': workload_score,
        'total': round(total_score, 2)
    }
```

**WHY THESE WEIGHTS:**
- **Skill (35%):** Most important - wrong skill = failed task
- **Availability (20%):** Must be free to accept
- **Location (20%):** Reduces travel, increases efficiency
- **Rating (15%):** Quality matters but not as much as ability
- **Workload (10%):** Tie-breaker for load balancing

### 🎯 Skill Validation System
**File:** `core/models.py` (Lines 59-133)

```python
class StudentSkill(models.Model):
    SKILL_CHOICES = [
        ('typing', 'Typing'),
        ('powerpoint', 'PowerPoint'),
        ('graphics', 'Graphics Design'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=20, choices=SKILL_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    test_score = models.IntegerField(null=True, blank=True)  # For typing test
    
    def save(self, *args, **kwargs):
        # Auto-update user's doer_type when skill is verified
        if self.status == 'verified':
            user = self.student
            if user.doer_type in ['microtasker', None]:
                user.doer_type = 'both'  # Can do skilled + microtasks
                user.save(update_fields=['doer_type'])
```

**WHY:** When a skill is verified, the user's `doer_type` automatically upgrades from 'microtasker' to 'both', unlocking access to specialized tasks.

### 📝 Application System with Fair Ranking
**File:** `core/models.py` (Lines 375-439)

```python
class TaskApplication(models.Model):
    # Snapshot stats at application time (prevents gaming the system)
    doer_rating_snapshot = models.DecimalField(max_digits=3, decimal_places=2)
    doer_completed_tasks_snapshot = models.IntegerField(default=0)
    doer_is_newbie = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # First time creating
            self.doer_rating_snapshot = self.doer.avg_rating
            completed_count = Task.objects.filter(
                doer=self.doer, 
                status='completed'
            ).count()
            self.doer_completed_tasks_snapshot = completed_count
            self.doer_is_newbie = completed_count < 3
        super().save(*args, **kwargs)
    
    @property
    def ranking_score(self):
        score = (self.doer_rating_snapshot * 10) + 
                (self.doer_completed_tasks_snapshot * 2)
        
        # NEWBIE BONUS: +15 points if < 3 completed tasks
        if self.doer_is_newbie:
            score += 15
        
        return score
```

**WHY THE NEWBIE BONUS:**
- Without it: Experienced doers always win, newbies never get a chance
- With +15 bonus: Newbie with 0 tasks gets 15 points, competitive with someone who has 5 tasks (5×2=10)
- This creates a fair marketplace where new users can build reputation

---

## OBJECTIVE 3: Secure Payment System (PayMongo Integration)

### 📋 What It Does
Processes payments via PayMongo API (GCash, Credit Cards). Implements 10% commission model with chat locking for revenue protection.

### 🔬 HOW & WHY IT WORKS

#### PayMongo API Client
**File:** `core/paymongo.py` (Lines 18-100)

```python
class PayMongoClient:
    def __init__(self):
        self.secret_key = settings.PAYMONGO_SECRET_KEY
        self.base_url = "https://api.paymongo.com/v1"
        
        # BASE64 AUTHENTICATION
        auth_string = f"{self.secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    def create_payment_intent(self, amount, description):
        # Convert to centavos (₱1 = 100 centavos)
        amount_centavos = int(float(amount) * 100)
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount_centavos,
                    "currency": "PHP",
                    "description": description,
                    "payment_method_allowed": ["card", "paymaya", "gcash"]
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/payment_intents",
            json=payload,
            headers=self.headers
        )
        
        return response.json() if response.status_code == 200 else None
```

**WHY BASE64 AUTH:**
PayMongo requires HTTP Basic Authentication. The secret key is base64-encoded and sent in the `Authorization` header. This is the standard OAuth 2.0 flow.

#### GCash Payment Source
**File:** `core/paymongo.py` (Lines 102-160)

```python
def create_source(self, amount, source_type="gcash", success_url=None, failed_url=None):
    amount_centavos = int(float(amount) * 100)
    
    payload = {
        "data": {
            "attributes": {
                "amount": amount_centavos,
                "currency": "PHP",
                "type": source_type,  # "gcash" or "paymaya"
                "redirect": {
                    "success": success_url,
                    "failed": failed_url
                }
            }
        }
    }
    
    response = requests.post(
        f"{self.base_url}/sources",
        json=payload,
        headers=self.headers,
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
```

**HOW GCASH WORKS:**
1. System calls `create_source(amount=110, type="gcash")`
2. PayMongo returns a `checkout_url`
3. User is redirected to PayMongo's hosted GCash page
4. User authenticates with GCash app
5. PayMongo sends webhook to confirm payment
6. System unlocks chat

#### 10% Commission Model
**File:** `core/paymongo.py` (Lines 338-377)

```python
def create_task_payment(self, task, payer, receiver):
    # ADD-ON MODEL: Poster pays Task Price + 10% Fee
    task_price = float(task.price)
    service_fee = task_price * 0.10
    total_amount = task_price + service_fee  # e.g., 100 + 10 = 110
    
    payment_intent = self.paymongo.create_payment_intent(
        amount=total_amount,
        description=f"Task Payment: {task.title} (incl. Service Fee)"
    )
    
    if payment_intent:
        # Store TOTAL amount (110)
        # Model's save() will split it: 100 (net) + 10 (commission)
        payment = Payment.objects.create(
            task=task,
            payer=payer,
            receiver=receiver,
            amount=total_amount,  # 110
            method='paymongo'
        )
```

#### Payment Model with Auto-Split Logic
**File:** `core/models.py` (Lines 488-512)

```python
class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        if self.commission_amount is None or self.net_amount == 0:
            from decimal import Decimal
            
            # REVERSE CALCULATION
            # Total = 110 | We need: Net = 100, Commission = 10
            # Formula: Net = Total / 1.10
            total_amount = Decimal(str(self.amount))
            self.net_amount = total_amount / Decimal('1.10')
            self.commission_amount = total_amount - self.net_amount
            
            # Round to 2 decimals
            self.net_amount = self.net_amount.quantize(Decimal('0.01'))
            self.commission_amount = self.commission_amount.quantize(Decimal('0.01'))
        
        super().save(*args, **kwargs)
```

**WHY THIS LOGIC:**
- If we store 110, the model calculates: 110 / 1.10 = 100 (net), 110 - 100 = 10 (commission)
- This ensures the doer ALWAYS gets the exact task price they agreed to
- The poster pays the extra 10% on top

### 🔒 Chat Lock Security Feature
**File:** `core/views.py` (Lines 588-625)

```python
def check_chat_access(task_id, user):
    task = Task.objects.get(id=task_id)
    
    # Only poster and doer can chat
    if user not in [task.poster, task.doer]:
        return {'allowed': False, 'reason': 'Not authorized'}
    
    # SECURITY: Require commission payment BEFORE ANY messages
    if not task.commission_deducted:
        return {
            'allowed': False,
            'reason': f'Pay ₱{task.commission_amount} commission to unlock chat',
            'requires_payment': True,
            'payment_url': reverse('payment_commission', args=[task.id])
        }
    
    # Commission paid - unlimited chat allowed
    return {'allowed': True, 'commission_paid': True}
```

**WHY THIS PREVENTS BYPASS:**
- Without chat lock: Users exchange phone numbers in free messages → complete transaction off-platform
- With chat lock: Users MUST pay commission first → platform revenue secured
- Once paid: Unlimited messaging (no per-message fees)

---

## OBJECTIVE 4: Task Monitoring & Rating/Feedback System

### 📋 What It Does
Provides role-specific dashboards (Poster vs. Doer) with real-time statistics and enforces payment-before-rating workflow.

### 🔬 HOW & WHY IT WORKS

#### Role-Based Monitoring Dashboard
**File:** `core/views.py` (Lines 2739-2814)

```python
@login_required
def task_monitoring(request):
    user = request.user
    
    if user.role == 'task_poster':
        # POSTER VIEW: Tasks I created
        tasks = Task.objects.filter(poster=user).select_related('doer')
        
        # Add rating status for each task
        for task in tasks:
            if task.status == 'completed' and task.doer:
                task.user_has_rated = Rating.objects.filter(
                    task=task,
                    rater=user,
                    rated=task.doer
                ).exists()
        
        # Calculate statistics
        stats = {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'pending': tasks.filter(status='open').count(),
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
        
    elif user.role == 'task_doer':
        # DOER VIEW: Tasks assigned to me
        tasks = Task.objects.filter(doer=user).select_related('poster')
        
        for task in tasks:
            if task.status == 'completed' and task.poster:
                task.user_has_rated = Rating.objects.filter(
                    task=task,
                    rater=user,
                    rated=task.poster
                ).exists()
```

**WHY SEPARATE VIEWS:**
- Posters need to see: "Which of MY posted tasks are complete?"
- Doers need to see: "Which tasks ASSIGNED TO ME are complete?"
- Different metrics, different workflows

#### Payment-Enforced Rating System
**File:** `core/views.py` (Lines 2817-2946)

```python
@login_required
def rate_user(request, task_id, user_id):
    task = get_object_or_404(Task, id=task_id)
    
    # PAYMENT ENFORCEMENT FOR RATING
    if request.user == task.poster and rated_user == task.doer:
        # Check if commission is paid
        if not task.chat_unlocked:
            messages.error(request, "You must pay the 10% system fee before rating.")
            return redirect('payment_system_fee', task_id=task_id)
        
        # Check doer payment
        payment = Payment.objects.filter(
            task=task,
            payer=request.user,
            receiver=task.doer
        ).first()
        
        if task.payment_method == 'online':
            if not payment or payment.status != 'confirmed':
                messages.error(request, "You must pay the task doer before rating.")
                return redirect('payment_task_doer', task_id=task_id)
    
    # RATING SUBMISSION & LIVE UPDATE
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.task = task
            rating.rater = request.user
            rating.rated = rated_user
            rating.save()
            
            # RECALCULATE AVERAGE RATING
            all_ratings = Rating.objects.filter(rated=rated_user)
            avg_rating = all_ratings.aggregate(Avg('score'))['score__avg']
            rated_user.avg_rating = round(avg_rating, 2)
            rated_user.total_ratings = all_ratings.count()
            rated_user.save()
```

**WHY PAYMENT ENFORCEMENT:**
- Prevents "rate and run" (poster rates poorly to avoid payment)
- Ensures doers get paid before feedback
- Creates accountability loop

---

# PART 2: ADDITIONAL INNOVATIVE FEATURES

## Feature 1: 3-Minute Application Window
**File:** `core/views.py` (Lines 361-383)

**WHAT:** After first application arrives, task stays visible for 3 minutes to allow other doers to apply.  
**WHY:** Gives newbies a fair chance. Without this, first applicant always wins.

## Feature 2: Smart Task Matching
**File:** `core/views.py` (Lines 329-502)

**WHAT:** Doers only see tasks they're qualified for based on verified skills.  
**WHY:** Prevents skill mismatch. Typing tasks only show to verified typists.

## Feature 3: System Wallet Revenue Tracking
**File:** `core/models.py` (Lines 670-713)

**WHAT:** Singleton model that tracks all platform commission revenue.  
**WHY:** Business analytics. Shows total earnings from 10% commissions.

---

# PART 3: CAPSTONE-WORTHY ELEMENTS

## 1. **Complex Multi-Factor Algorithm**
The 7-factor prioritization demonstrates database-level computations, weighted scoring, and real-time aggregation.

## 2. **Third-Party API Integration**
PayMongo integration shows OAuth 2.0, webhook security (HMAC), and financial data handling.

## 3. **Revenue Protection Innovation**
The chat-lock system is a novel solution to the "platform bypass" problem in gig economy platforms.

## 4. **Fair Marketplace Design**
Multiple features ensure fairness: newbie bonus, 3-minute window, skill filtering, payment enforcement.

## 5. **Performance Optimization**
Database-level computations, prefetch queries, indexed fields, connection pooling.

## 6. **Security Best Practices**
CSRF, XSS prevention, SQL injection prevention, webhook verification, password hashing.

## 7. **Real-World Application**
Solves actual gig economy problems: trust, quality, fairness, revenue, efficiency.

---

# DEFENSE Q&A PREPARATION

### Q: "How does the prioritization algorithm work?"
**A:** "We use a 7-factor weighted scoring system at the database level. Tasks are scored on urgency (1.5×), location (2.0×), preferences (2.0×), time windows (1.5×), price (1.0×), rating (2.0×), and deadline (1.0×). Computation happens in PostgreSQL using Django's `annotate` with `Case/When`, which is faster than Python loops. Maximum possible score is 11.0 points."

### Q: "Why did you use a chat lock?"
**A:** "We identified a business risk: users could exchange contact info in free messages and transact off-platform. The solution: require 10% commission payment BEFORE the first message. This is implemented in `check_chat_access`, which checks `task.commission_deducted`. Once paid, messaging is unlimited."

### Q: "How does the newbie bonus ensure fairness?"
**A:** "New doers (< 3 tasks) get a +15 point bonus. A veteran with 5 tasks gets 10 points (5×2), so the bonus makes newbies competitive. This solves the cold-start problem where new users can't get tasks without experience."

### Q: "What makes this a capstone-level project?"
**A:** "Three things: Technical complexity (Django, PostgreSQL, PayMongo, real-time calculations), innovation (chat-lock revenue protection), and real-world applicability (solves actual gig economy problems with measurable business value - 10% commission on every transaction)."
