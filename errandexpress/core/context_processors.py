# core/context_processors.py
from django.db.models import Avg, Sum, Count, Q
from decimal import Decimal


def user_stats(request):
    """
    Context processor to provide real user statistics to all templates
    """
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    stats = {
        'tasks_completed': 0,
        'user_rating': 0,
        'total_earned': 0,
        'active_tasks': 0,
    }
    
    try:
        from .models import Task, Rating, Payment
        
        # Tasks completed (different logic for poster vs doer)
        if user.role == 'task_doer':
            # For doers: tasks they completed
            stats['tasks_completed'] = Task.objects.filter(
                doer=user,
                status='completed'
            ).count()
            
            # Total earned from completed tasks (receiver in Payment model)
            total_earned = Payment.objects.filter(
                receiver=user,
                status='confirmed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            stats['total_earned'] = float(total_earned)
            
            # Active tasks (accepted or in progress)
            stats['active_tasks'] = Task.objects.filter(
                doer=user,
                status__in=['accepted', 'in_progress']
            ).count()
            
        elif user.role == 'task_poster':
            # For posters: tasks they posted that were completed
            stats['tasks_completed'] = Task.objects.filter(
                poster=user,
                status='completed'
            ).count()
            
            # Total spent on completed tasks (payer in Payment model)
            total_spent = Payment.objects.filter(
                payer=user,
                status='confirmed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            stats['total_earned'] = float(total_spent)
            
            # Active tasks (open or in progress)
            stats['active_tasks'] = Task.objects.filter(
                poster=user,
                status__in=['open', 'accepted', 'in_progress']
            ).count()
        
        # User rating (average of all ratings received)
        avg_rating = Rating.objects.filter(
            rated=user
        ).aggregate(avg=Avg('score'))['avg']
        
        if avg_rating:
            stats['user_rating'] = round(float(avg_rating), 1)
        else:
            stats['user_rating'] = 0
            
        # Unread Notifications Count
        stats['unread_notifications_count'] = 0
        try:
            from .models import Notification
            stats['unread_notifications_count'] = Notification.objects.filter(
                user=user, 
                is_read=False
            ).count()
        except Exception:
            pass

        # Unread Messages Count
        stats['unread_messages_count'] = 0
        try:
            from .models import Message
            # Count unread messages in tasks where user is poster or doer, sent by others
            stats['unread_messages_count'] = Message.objects.filter(
                Q(task__poster=user) | Q(task__doer=user),
                is_read=False
            ).exclude(sender=user).count()
        except Exception:
            pass
            
    except Exception as e:
        # If there's an error, return default values
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculating user stats: {str(e)}")
    
    return {'user_stats': stats}
