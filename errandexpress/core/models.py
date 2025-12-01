from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Extended user model for ErrandExpress"""
    ROLE_CHOICES = [
        ('task_poster', 'Task Poster'),
        ('task_doer', 'Task Doer'),
        ('admin', 'Admin'),
    ]
    
    DOER_TYPE_CHOICES = [
        ('microtasker', 'Microtasker'),
        ('skilled', 'Skilled Worker'),
        ('both', 'Both'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='task_doer')
    doer_type = models.CharField(max_length=20, choices=DOER_TYPE_CHOICES, null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.fullname} ({self.role})"
    
    def update_rating(self, new_rating):
        """Update user's average rating"""
        total_score = self.avg_rating * self.total_ratings + new_rating
        self.total_ratings += 1
        self.avg_rating = total_score / self.total_ratings
        self.save()


class StudentSkill(models.Model):
    """Skills validation for task doers"""
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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=20, choices=SKILL_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    proof_url = models.FileField(upload_to='skill_proofs/', null=True, blank=True)
    test_score = models.IntegerField(null=True, blank=True)  # For typing test
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_skills')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'skill_name']
    
    def __str__(self):
        return f"{self.student.fullname} - {self.skill_name} ({self.status})"


class Task(models.Model):
    """Task/Errand model"""
    CATEGORY_CHOICES = [
        ('microtask', 'Microtask'),
        ('typing', 'Typing'),
        ('powerpoint', 'PowerPoint'),
        ('graphics', 'Graphics Design'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_tasks')
    doer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tags = models.CharField(max_length=255, help_text="Comma-separated tags")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    location = models.CharField(max_length=255, blank=True)
    requirements = models.TextField(blank=True)
    chat_unlocked = models.BooleanField(default=False)  # Chat unlocked after ₱2 payment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.poster.fullname}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['poster']),
            models.Index(fields=['doer']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]


class Message(models.Model):
    """Chat messages between poster and doer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_proof = models.BooleanField(default=False)  # Mark as task proof
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['sender']),
            models.Index(fields=['created_at']),
            models.Index(fields=['task', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.fullname}: {self.message[:50]}..."


class SystemCommission(models.Model):
    """Track ₱2 system fees"""
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='commission')
    payer = models.ForeignKey(User, on_delete=models.CASCADE)  # Task poster
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=2.00)
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paymongo_payment_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"₱{self.amount} - {self.task.title} ({self.status})"


class Rating(models.Model):
    """Rating and feedback system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rated = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['task', 'rater', 'rated']
    
    def __str__(self):
        return f"{self.rater.fullname} rated {self.rated.fullname}: {self.score}/10"


class Report(models.Model):
    """User reports system"""
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('fraud', 'Fraud'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('scam', 'Scam'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Report: {self.reporter.fullname} -> {self.reported.fullname} ({self.reason})"


class TaskApplication(models.Model):
    """Applications from task doers to tasks - solves the multiple applicants problem"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='applications')
    doer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_applications')
    
    # Application details
    cover_letter = models.TextField(help_text="Why are you a good fit for this task?")
    proposed_timeline = models.CharField(max_length=100, blank=True, help_text="When can you complete this?")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Snapshot of doer stats at time of application (for fair comparison)
    doer_rating_snapshot = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    doer_completed_tasks_snapshot = models.IntegerField(default=0)
    doer_is_newbie = models.BooleanField(default=False, help_text="True if doer has < 3 completed tasks")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Track first application time for 3-minute window
    first_application_time = models.DateTimeField(null=True, blank=True, help_text="Time when first application was received")
    
    class Meta:
        unique_together = ['task', 'doer']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['doer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.doer.fullname} → {self.task.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Snapshot doer stats when first creating application
        if not self.pk:
            self.doer_rating_snapshot = self.doer.avg_rating
            completed_count = Task.objects.filter(doer=self.doer, status='completed').count()
            self.doer_completed_tasks_snapshot = completed_count
            self.doer_is_newbie = completed_count < 3
        super().save(*args, **kwargs)
    
    @property
    def ranking_score(self):
        """
        Smart ranking algorithm that gives newbies a fair chance
        Score = (Rating × 10) + (Completed Tasks × 2) + (Newbie Bonus)
        """
        score = (self.doer_rating_snapshot * 10) + (self.doer_completed_tasks_snapshot * 2)
        
        # Newbie bonus: If < 3 tasks, add 15 points to compete with experienced doers
        if self.doer_is_newbie:
            score += 15
        
        return score


class Payment(models.Model):
    """Payment proofs and tracking"""
    METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('bank_transfer', 'Bank Transfer'),
        ('paymongo', 'PayMongo'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('pending_payment', 'Pending Payment'),  # Waiting for online payment
        ('pending_confirmation', 'Pending Confirmation'),  # Waiting for manual confirmation (COD)
        ('confirmed', 'Confirmed'),
        ('disputed', 'Disputed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='payment')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 10% commission
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Amount after commission
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    proof_url = models.FileField(upload_to='payment_proofs/', null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    paymongo_payment_id = models.CharField(max_length=255, blank=True, unique=True)  # Prevent duplicates
    paymongo_source_id = models.CharField(max_length=255, blank=True)  # For GCash/Card sources
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # Prevent duplicate payments for same task
        unique_together = ('task', 'payer', 'receiver')
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['payer', '-created_at']),
            models.Index(fields=['receiver', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Calculate commission and net amount before saving"""
        if not self.commission_amount:
            # Convert to Decimal to handle type properly
            from decimal import Decimal
            commission_rate = Decimal('0.10')
            self.commission_amount = self.amount * commission_rate  # 10% commission
            self.net_amount = self.amount - self.commission_amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"₱{self.amount} - {self.task.title} ({self.status})"


class Notification(models.Model):
    """System notifications"""
    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('payment_received', 'Payment Received'),
        ('rating_received', 'Rating Received'),
        ('skill_verified', 'Skill Verified'),
        ('report_filed', 'Report Filed'),
        ('system_message', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.fullname}: {self.title}"


class AdminLog(models.Model):
    """Admin action audit trail"""
    ACTION_CHOICES = [
        ('skill_approved', 'Skill Approved'),
        ('skill_rejected', 'Skill Rejected'),
        ('user_banned', 'User Banned'),
        ('user_unbanned', 'User Unbanned'),
        ('user_warned', 'User Warned'),
        ('report_reviewed', 'Report Reviewed'),
        ('report_resolved', 'Report Resolved'),
        ('report_dismissed', 'Report Dismissed'),
        ('task_deleted', 'Task Deleted'),
        ('payment_refunded', 'Payment Refunded'),
        ('system_config', 'System Configuration Changed'),
        ('other', 'Other Action'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_received')
    target_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    target_skill = models.ForeignKey(StudentSkill, on_delete=models.SET_NULL, null=True, blank=True)
    target_report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(help_text="Detailed description of the action taken")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['admin', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        admin_name = self.admin.fullname if self.admin else "System"
        return f"{admin_name} - {self.get_action_display()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TaskAssignment(models.Model):
    """Track task assignments with assignment history and status"""
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending Assignment'),
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted by Agent'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reassigned', 'Reassigned'),
        ('cancelled', 'Cancelled'),
    ]
    
    ASSIGNMENT_METHOD_CHOICES = [
        ('automatic', 'Automatic Assignment'),
        ('manual', 'Manual Assignment'),
        ('application', 'Agent Application'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    assignment_method = models.CharField(max_length=20, choices=ASSIGNMENT_METHOD_CHOICES, default='automatic')
    
    # Assignment criteria matching scores
    skill_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    availability_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    rating_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    workload_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reassigned_at = models.DateTimeField(null=True, blank=True)
    
    # Notes and reasons
    assignment_notes = models.TextField(blank=True, help_text="Reason for assignment")
    reassignment_reason = models.TextField(blank=True, help_text="Reason for reassignment")
    
    class Meta:
        ordering = ['-assigned_at']
        unique_together = ('task', 'agent')  # One assignment per task-agent pair
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['-assigned_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.task.title} → {self.agent.fullname} ({self.get_status_display()})"
    
    def accept_assignment(self):
        """Agent accepts the assignment"""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
    
    def start_assignment(self):
        """Agent starts working on the task"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete_assignment(self):
        """Mark assignment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def reassign(self, reason=''):
        """Mark assignment as reassigned"""
        self.status = 'reassigned'
        self.reassigned_at = timezone.now()
        self.reassignment_reason = reason
        self.save()


class SystemWallet(models.Model):
    """Track system revenue from ₱2 system fees"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_transactions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Wallet"
        verbose_name_plural = "System Wallet"
    
    def __str__(self):
        return f"System Wallet - ₱{self.total_revenue} ({self.total_transactions} transactions)"
    
    @classmethod
    def get_or_create_wallet(cls):
        """Get or create the system wallet"""
        wallet, created = cls.objects.get_or_create(id='00000000-0000-0000-0000-000000000000')
        if created:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("✅ System Wallet created")
        return wallet
    
    def add_revenue(self, amount, description=""):
        """Add revenue to wallet"""
        # Convert amount to Decimal to avoid type mismatch
        from decimal import Decimal
        amount = Decimal(str(amount))
        
        # Ensure total_revenue is Decimal
        if isinstance(self.total_revenue, float):
            self.total_revenue = Decimal(str(self.total_revenue))
        
        self.total_revenue += amount
        self.total_transactions += 1
        self.save()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"💰 Revenue added: ₱{amount} - {description}")
        logger.info(f"Total wallet: ₱{self.total_revenue} ({self.total_transactions} transactions)")
