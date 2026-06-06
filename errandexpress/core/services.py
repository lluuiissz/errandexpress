"""
Prioritization Service for ErrandExpress
Implements automatic task prioritization based on multiple factors
"""

from django.db.models import Q, F, Value, Case, When, DecimalField, IntegerField, Avg, Count, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta


class PrioritizationService:
    """
    Service for calculating task priority scores based on multiple factors:
    1. Urgency (priority_level 1-5)
    2. Location proximity (campus_location match)
    3. Customer preferences (preferred_doer)
    4. Time window match
    5. Price agreement
    6. User ratings
    7. Deadline urgency
    """
    
    # Scoring weights
    URGENCY_WEIGHT = Decimal('1.5')
    LOCATION_WEIGHT = Decimal('2.0')
    PREFERENCE_WEIGHT = Decimal('2.0')
    TIME_WINDOW_WEIGHT = Decimal('1.5')
    PRICE_WEIGHT = Decimal('1.0')
    RATING_WEIGHT = Decimal('2.0')
    DEADLINE_WEIGHT = Decimal('1.0')
    
    @staticmethod
    def calculate_urgency_score(priority_level):
        """
        Calculate urgency score based on priority level (1-5)
        Returns: 0.0 to 1.5
        """
        return Case(
            When(priority_level=5, then=Value(Decimal('1.50'))),
            When(priority_level=4, then=Value(Decimal('1.20'))),
            When(priority_level=3, then=Value(Decimal('0.90'))),
            When(priority_level=2, then=Value(Decimal('0.60'))),
            When(priority_level=1, then=Value(Decimal('0.30'))),
            default=Value(Decimal('0.90')),  # Default to normal priority
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    
    @staticmethod
    def calculate_location_score(user_campus):
        """
        Calculate location match score
        Returns: 0.0 or 2.0
        """
        return Case(
            When(campus_location=user_campus, then=Value(Decimal('2.00'))),
            When(campus_location='', then=Value(Decimal('0.50'))),  # No location specified
            default=Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    
    @staticmethod
    def calculate_preference_score(user_id):
        """
        Calculate customer preference match score
        Returns: 0.0 or 2.0
        """
        return Case(
            When(preferred_doer_id=user_id, then=Value(Decimal('2.00'))),
            default=Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    
    @staticmethod
    def calculate_time_window_score():
        """
        Calculate time window match score
        Returns: 0.0 to 1.5
        """
        now = timezone.now()
        
        return Case(
            # Within preferred time window - highest score
            When(
                time_window_start__lte=now,
                time_window_end__gte=now,
                then=Value(Decimal('1.50'))
            ),
            # Same day as time window start - medium score
            When(
                time_window_start__date=now.date(),
                then=Value(Decimal('1.00'))
            ),
            # Flexible timing - low score
            When(
                flexible_timing=True,
                then=Value(Decimal('0.50'))
            ),
            # No time window specified - neutral
            When(
                time_window_start__isnull=True,
                then=Value(Decimal('0.30'))
            ),
            default=Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    
    @staticmethod
    def calculate_price_score():
        """
        Calculate price-based score (normalized)
        Higher prices get higher scores
        Returns: 0.0 to 1.0
        """
        # Normalize price: score = min(price / 1000, 1.0)
        # Tasks priced at ₱1000+ get max score
        return ExpressionWrapper(
            Case(
                When(price__gte=1000, then=Value(Decimal('1.00'))),
                When(price__gte=500, then=F('price') / Value(Decimal('1000.0'))),
                When(price__gte=100, then=F('price') / Value(Decimal('2000.0'))),
                default=F('price') / Value(Decimal('5000.0')),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            ),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    
    @staticmethod
    def calculate_deadline_urgency_score():
        """
        Calculate deadline urgency score
        Returns: 0.2 to 1.0
        """
        now = timezone.now()
        one_day = now + timedelta(days=1)
        three_days = now + timedelta(days=3)
        one_week = now + timedelta(days=7)
        
        return Case(
            # Due within 24 hours - URGENT
            When(deadline__lte=one_day, then=Value(Decimal('1.00'))),
            # Due within 3 days - High priority
            When(deadline__lte=three_days, then=Value(Decimal('0.70'))),
            # Due within 1 week - Medium priority
            When(deadline__lte=one_week, then=Value(Decimal('0.40'))),
            # Due later - Low priority
            default=Value(Decimal('0.20')),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    
    @classmethod
    def get_prioritized_tasks(cls, tasks_queryset, user):
        """
        Apply prioritization scoring to a task queryset
        
        Args:
            tasks_queryset: Django QuerySet of Task objects
            user: User object for personalized scoring
            
        Returns:
            QuerySet with priority_score annotation, ordered by score DESC
        """
        from core.models import Rating
        from django.db.models import OuterRef, Subquery
        
        # Calculate poster rating from Rating table
        poster_rating_subquery = Rating.objects.filter(
            rated=OuterRef('poster')
        ).values('rated').annotate(
            avg_rating=Avg('score')
        ).values('avg_rating')
        
        # Apply all scoring factors
        prioritized_tasks = tasks_queryset.annotate(
            # Individual factor scores
            urgency_factor=cls.calculate_urgency_score(F('priority_level')),
            location_factor=cls.calculate_location_score(user.campus_location),
            preference_factor=cls.calculate_preference_score(user.id),
            time_window_factor=cls.calculate_time_window_score(),
            price_factor=cls.calculate_price_score(),
            deadline_factor=cls.calculate_deadline_urgency_score(),
            
            # Poster rating factor
            poster_rating_value=Coalesce(
                Subquery(poster_rating_subquery, output_field=DecimalField(max_digits=4, decimal_places=2)),
                Value(Decimal('3.00'), output_field=DecimalField(max_digits=4, decimal_places=2)),
                output_field=DecimalField(max_digits=4, decimal_places=2)
            ),
            rating_factor=ExpressionWrapper(
                (F('poster_rating_value') / Value(Decimal('5.00'))) * cls.RATING_WEIGHT,
                output_field=DecimalField(max_digits=5, decimal_places=2)
            ),
            
            # Calculate total priority score
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
        
        return prioritized_tasks
    
    @classmethod
    def get_score_breakdown(cls, task, user):
        """
        Get detailed score breakdown for a specific task
        Useful for debugging and transparency
        
        Returns:
            dict with individual factor scores and total
        """
        from core.models import Rating
        
        # Calculate each factor manually for this task
        urgency = (task.priority_level / 5.0) * float(cls.URGENCY_WEIGHT)
        
        location = float(cls.LOCATION_WEIGHT) if task.campus_location == user.campus_location else 0.0
        
        preference = float(cls.PREFERENCE_WEIGHT) if task.preferred_doer_id == user.id else 0.0
        
        # Time window
        now = timezone.now()
        if task.time_window_start and task.time_window_end:
            if task.time_window_start <= now <= task.time_window_end:
                time_window = 1.5
            elif task.time_window_start.date() == now.date():
                time_window = 1.0
            else:
                time_window = 0.0
        elif task.flexible_timing:
            time_window = 0.5
        else:
            time_window = 0.3
        time_window *= float(cls.TIME_WINDOW_WEIGHT)
        
        # Price
        price = min(float(task.price) / 1000.0, 1.0) * float(cls.PRICE_WEIGHT)
        
        # Rating
        poster_ratings = Rating.objects.filter(rated=task.poster)
        avg_rating = poster_ratings.aggregate(Avg('score'))['score__avg'] or 3.0
        rating = (avg_rating / 5.0) * float(cls.RATING_WEIGHT)
        
        # Deadline
        days_until = (task.deadline - now).days
        if days_until <= 1:
            deadline = 1.0
        elif days_until <= 3:
            deadline = 0.7
        elif days_until <= 7:
            deadline = 0.4
        else:
            deadline = 0.2
        deadline *= float(cls.DEADLINE_WEIGHT)
        
        total = urgency + location + preference + time_window + price + rating + deadline
        
        return {
            'urgency_score': round(urgency, 2),
            'location_score': round(location, 2),
            'preference_score': round(preference, 2),
            'time_window_score': round(time_window, 2),
            'price_score': round(price, 2),
            'rating_score': round(rating, 2),
            'deadline_score': round(deadline, 2),
            'total_score': round(total, 2),
            'max_possible_score': round(float(
                cls.URGENCY_WEIGHT + cls.LOCATION_WEIGHT + cls.PREFERENCE_WEIGHT +
                cls.TIME_WINDOW_WEIGHT + cls.PRICE_WEIGHT + cls.RATING_WEIGHT +
                cls.DEADLINE_WEIGHT
            ), 2)
        }
