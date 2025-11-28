"""
Celery tasks for ErrandExpress
Handles background jobs like deadline reminders, payment retries, etc.
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_deadline_reminders():
    """
    Send reminders to task doers 24 hours before deadline
    Runs every hour (configured in celery beat schedule)
    """
    from .models import Task, Notification
    
    try:
        # Find tasks that are in_progress and deadline is within 24 hours
        now = timezone.now()
        deadline_window_start = now + timedelta(hours=23)
        deadline_window_end = now + timedelta(hours=25)
        
        tasks_to_remind = Task.objects.filter(
            status='in_progress',
            deadline__gte=deadline_window_start,
            deadline__lte=deadline_window_end
        ).select_related('doer', 'poster')
        
        reminder_count = 0
        for task in tasks_to_remind:
            # Check if reminder already sent (by checking for existing notification)
            existing_reminder = Notification.objects.filter(
                user=task.doer,
                type='deadline_reminder',
                related_task=task
            ).exists()
            
            if not existing_reminder and task.doer:
                # Send reminder to doer
                Notification.objects.create(
                    user=task.doer,
                    type='deadline_reminder',
                    title=f'⏰ Task Deadline in 24 Hours',
                    message=f'"{task.title}" is due in 24 hours. Complete it before {task.deadline.strftime("%I:%M %p")}',
                    related_task=task
                )
                reminder_count += 1
        
        logger.info(f"Sent {reminder_count} deadline reminders")
        return {'success': True, 'reminders_sent': reminder_count}
        
    except Exception as e:
        logger.error(f"Error sending deadline reminders: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def handle_overdue_tasks():
    """
    Handle tasks that have passed their deadline without completion
    Runs every hour
    """
    from .models import Task, Notification
    
    try:
        now = timezone.now()
        
        # Find overdue tasks that are still in_progress
        overdue_tasks = Task.objects.filter(
            status='in_progress',
            deadline__lt=now
        ).select_related('doer', 'poster')
        
        overdue_count = 0
        for task in overdue_tasks:
            # Check if overdue notification already sent
            existing_notification = Notification.objects.filter(
                user=task.poster,
                type='task_overdue',
                related_task=task
            ).exists()
            
            if not existing_notification:
                # Notify poster that task is overdue
                Notification.objects.create(
                    user=task.poster,
                    type='task_overdue',
                    title='⚠️ Task Overdue',
                    message=f'"{task.title}" is overdue. Contact the doer or mark as incomplete.',
                    related_task=task
                )
                overdue_count += 1
        
        logger.info(f"Marked {overdue_count} tasks as overdue")
        return {'success': True, 'overdue_tasks': overdue_count}
        
    except Exception as e:
        logger.error(f"Error handling overdue tasks: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def retry_failed_payments():
    """
    Retry failed payment transactions
    Runs every 30 minutes
    """
    from .models import Payment
    
    try:
        # Find failed payments that haven't been retried recently
        failed_payments = Payment.objects.filter(
            status='failed',
            updated_at__lt=timezone.now() - timedelta(hours=1)
        ).select_related('task')
        
        retry_count = 0
        for payment in failed_payments:
            try:
                # Log retry attempt
                logger.info(f"Retrying payment {payment.id} for task {payment.task.id}")
                
                # Mark as pending for manual retry
                payment.status = 'pending_payment'
                payment.save()
                retry_count += 1
                
            except Exception as e:
                logger.error(f"Error retrying payment {payment.id}: {str(e)}")
        
        logger.info(f"Retried {retry_count} failed payments")
        return {'success': True, 'retried_payments': retry_count}
        
    except Exception as e:
        logger.error(f"Error in retry_failed_payments: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def reconcile_pending_payments():
    """
    Reconcile pending payments with PayMongo
    Runs every 30 minutes
    """
    from .models import Payment
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Find payments pending for more than 1 hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        pending_payments = Payment.objects.filter(
            status='pending',
            created_at__lt=one_hour_ago,
            paymongo_payment_id__isnull=False
        )
        
        reconciled_count = 0
        for payment in pending_payments:
            try:
                # Verify payment with PayMongo
                from .paymongo import PayMongoClient
                client = PayMongoClient()
                payment_intent = client.retrieve_payment_intent(payment.paymongo_payment_id)
                
                if payment_intent:
                    status = payment_intent['data']['attributes']['status']
                    if status == 'succeeded':
                        payment.status = 'confirmed'
                        payment.confirmed_at = timezone.now()
                        payment.save()
                        reconciled_count += 1
                        logger.info(f"Payment {payment.id} reconciled: {status}")
                        
            except Exception as e:
                logger.error(f"Error reconciling payment {payment.id}: {str(e)}")
        
        logger.info(f"Payment reconciliation complete: {reconciled_count} payments updated")
        return {'success': True, 'reconciled_payments': reconciled_count}
        
    except Exception as e:
        logger.error(f"Payment reconciliation error: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_notifications():
    """
    Delete old notifications (older than 30 days)
    Runs daily
    """
    from .models import Notification
    
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Deleted {deleted_count} old notifications")
        return {'success': True, 'deleted_notifications': deleted_count}
        
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {str(e)}")
        return {'success': False, 'error': str(e)}
