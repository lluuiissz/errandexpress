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
    Send deadline reminders with increasing frequency:
    - 24 hours before: Once
    - 2 hours before: Every 20 minutes
    - 20 minutes before: Every 2 minutes
    
    Runs every 2 minutes (via Celery beat)
    """
    from .models import Task, Notification
    
    try:
        now = timezone.now()
        
        # 1. Base Query: Open or In Progress tasks with future deadline
        active_tasks = Task.objects.filter(
            status__in=['open', 'in_progress'],
            deadline__gt=now
        ).select_related('doer', 'poster')
        
        reminders_sent = 0
        
        for task in active_tasks:
            time_remaining = task.deadline - now
            total_seconds = time_remaining.total_seconds()
            hours_remaining = total_seconds / 3600
            minutes_remaining = total_seconds / 60
            
            # Users to notify (Poster always, Doer if assigned)
            recipients = [task.poster]
            if task.doer:
                recipients.append(task.doer)
                
            notification_type = 'deadline_reminder'
            
            # --- TIER 1: CRITICAL (< 20 Minutes) ---
            if minutes_remaining < 20:
                for recipient in recipients:
                    # Check recent notifications (last 2 mins)
                    last_notif = Notification.objects.filter(
                        user=recipient,
                        type=notification_type,
                        related_task=task,
                        created_at__gte=now - timedelta(minutes=2)
                    ).exists()
                    
                    if not last_notif:
                        Notification.objects.create(
                            user=recipient,
                            type=notification_type,
                            title=f"ðŸš¨ CRITICAL: Due in {int(minutes_remaining)} mins!",
                            message=f"Task '{task.title}' is due very soon! Deadline: {task.deadline.strftime('%I:%M %p')}",
                            related_task=task
                        )
                        reminders_sent += 1

            # --- TIER 2: URGENT (< 2 Hours) ---
            elif hours_remaining < 2:
                for recipient in recipients:
                    # Check recent notifications (last 20 mins)
                    last_notif = Notification.objects.filter(
                        user=recipient,
                        type=notification_type,
                        related_task=task,
                        created_at__gte=now - timedelta(minutes=20)
                    ).exists()
                    
                    if not last_notif:
                        Notification.objects.create(
                            user=recipient,
                            type=notification_type,
                            title=f"â³ Urgent: Due in {int(minutes_remaining)} mins",
                            message=f"Head's up! Task '{task.title}' is due in under 2 hours.",
                            related_task=task
                        )
                        reminders_sent += 1

            # --- TIER 3: STANDARD (< 24 Hours) ---
            elif hours_remaining < 24:
                for recipient in recipients:
                    # Check if ANY deadline reminder sent in last 24h (to avoid spamming from previous checks)
                    # Actually, for 24h warning, we just want to ensure we notified at least once in this window
                    # But complicating filter: if we entered this block, we are > 2h away.
                    # So we just check if we ever sent a "24 Hour" specific warning? 
                    # Simpler: Check if ANY deadline reminder sent ever for this task? 
                    # Or specifically check if one sent in the last 24h.
                    
                    # Implementation: Check if we sent one recently (e.g. within 20h to be safe, or just check exclusivity)
                    # Let's check if we sent one in the last 24 hours at all.
                    has_notified_24h = Notification.objects.filter(
                        user=recipient,
                        type=notification_type,
                        related_task=task,
                        created_at__gte=now - timedelta(hours=24)
                    ).exists()
                    
                    if not has_notified_24h:
                        Notification.objects.create(
                            user=recipient,
                            type=notification_type,
                            title=f"â° Task Due Tomorrow",
                            message=f"Reminder: '{task.title}' is due in 24 hours ({task.deadline.strftime('%I:%M %p')})",
                            related_task=task
                        )
                        reminders_sent += 1

        if reminders_sent > 0:
            logger.info(f"Sent {reminders_sent} granular deadline reminders")
        
        return {'success': True, 'reminders_sent': reminders_sent}
        
    except Exception as e:
        logger.error(f"Error sending deadline reminders: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def handle_overdue_tasks():
    """
    Handle tasks that have passed their deadline without completion
    Runs every hour -> Should probably run more often now, but logic is idempotent.
    """
    from .models import Task, Notification, User
    
    try:
        now = timezone.now()
        
        # Find overdue tasks that are still in_progress or open
        overdue_tasks = Task.objects.filter(
            status__in=['open', 'in_progress'],
            deadline__lt=now
        ).select_related('doer', 'poster')
        
        overdue_count = 0
        
        # Fetch admins for alerting
        admins = User.objects.filter(role='admin', is_active=True)
        
        for task in overdue_tasks:
            # CHECK EXPIRED: Open & Overdue (No Doer assigned usually, or assigned but reverted)
            if task.status == 'open':
                # Notify Poster about Expiration
                existing_notification = Notification.objects.filter(
                    user=task.poster,
                    type='task_expired',
                    related_task=task
                ).exists()
                
                if not existing_notification:
                    Notification.objects.create(
                        user=task.poster,
                        type='task_expired',
                        title='â³ Task Expired',
                        message=f'No one applied for "{task.title}" before the deadline. Please Update or Delete it.',
                        related_task=task
                    )
                    overdue_count += 1
                continue # Skip standard overdue logic for expired tasks

            # STANDARD OVERDUE: In Progress (Has Doer)
            # 1. Notify Poster
            existing_notification = Notification.objects.filter(
                user=task.poster,
                type='task_overdue',
                related_task=task
            ).exists()
            
            if not existing_notification:
                Notification.objects.create(
                    user=task.poster,
                    type='task_overdue',
                    title='âš ï¸ Task Overdue',
                    message=f'"{task.title}" is now overdue. Please review.',
                    related_task=task
                )
                
                # 2. Notify Doer (if assigned)
                if task.doer:
                    Notification.objects.create(
                        user=task.doer,
                        type='task_overdue',
                        title='âš ï¸ You Missed a Deadline',
                        message=f'The deadline for "{task.title}" has passed. Please contact the poster immediately.',
                        related_task=task
                    )
                
                # 3. Alert Admins (Only once per overdue task)
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        type='system_alert', # Or 'task_overdue'
                        title='âš ï¸ Admin Alert: Task Overdue',
                        message=f'Task "{task.title}" (ID: {str(task.id)[:8]}) is overdue. Poster: {task.poster.fullname}',
                        related_task=task
                    )
                
                overdue_count += 1
                
        if overdue_count > 0:
            logger.info(f"Processed {overdue_count} new overdue/expired tasks")
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


@shared_task
def auto_delete_expired_tasks():
    """
    Auto-delete expired tasks (Open status + Deadline passed > 24 hours ago)
    Runs hourly
    """
    from .models import Task, Notification
    
    try:
        # Define grace period (24 hours after deadline)
        grace_period_end = timezone.now() - timedelta(hours=24)
        
        # Find tasks that are OPEN and DEADLINE was more than 24 hours ago
        expired_tasks = Task.objects.filter(
            status='open',
            deadline__lt=grace_period_end
        )
        
        deleted_count = 0
        
        for task in expired_tasks:
            # Notify Poster before deletion (or technically after, but we need the user obj)
            poster = task.poster
            task_title = task.title
            
            # Create notification
            Notification.objects.create(
                user=poster,
                type='system_message', 
                title='ðŸ—‘ï¸ Task Auto-Deleted',
                message=f'Your task "{task_title}" was automatically deleted because it was expired for more than 24 hours.',
            )
            
            # Delete the task
            task.delete()
            deleted_count += 1
            
        if deleted_count > 0:
            logger.info(f"Auto-deleted {deleted_count} expired tasks")
            
        return {'success': True, 'deleted_tasks': deleted_count}
        
    except Exception as e:
        logger.error(f"Error auto-deleting tasks: {str(e)}")
        return {'success': False, 'error': str(e)}
 
 @ s h a r e d _ t a s k  
 d e f   p r o c e s s _ t a s k _ a s s i g n m e n t s ( ) :  
         " " "  
         ð x¤    A U T O M A T E D   T A S K   A S S I G N M E N T   A G E N T  
         P e r i o d i c a l l y   c h e c k s   f o r   t a s k s   t h a t   a r e   r e a d y   f o r   a s s i g n m e n t .  
          
         L O G I C :  
         1 .   F i n d   ' o p e n '   t a s k s   w i t h   a u t o _ a s s i g n _ e n a b l e d = T r u e  
         2 .   C H E C K   3 - M I N U T E   W I N D O W :  
               -   I f   >   3   m i n s   s i n c e   f i r s t   a p p l i c a t i o n :  
                   - >   P i c k   b e s t   a p p l i c a n t   ( S m a r t   S e l e c t i o n )  
               -   I f   >   3   m i n s   a n d   N O   a p p l i c a n t s :  
                   - >   T r i g g e r   P u s h   A s s i g n m e n t   ( F i n d   a n y   a v a i l a b l e   a g e n t )  
         3 .   C r e a t e   a s s i g n m e n t   a n d   n o t i f y  
          
         R u n s   e v e r y   1   m i n u t e .  
         " " "  
         f r o m   . m o d e l s   i m p o r t   T a s k ,   T a s k A p p l i c a t i o n ,   T a s k A s s i g n m e n t  
          
         t r y :  
                 n o w   =   t i m e z o n e . n o w ( )  
                  
                 #   F i n d   c a n d i d a t e   t a s k s  
                 #   1 .   O p e n  
                 #   2 .   A u t o - a s s i g n   e n a b l e d  
                 #   3 .   N o   c u r r e n t   a s s i g n m e n t  
                 c a n d i d a t e _ t a s k s   =   T a s k . o b j e c t s . f i l t e r (  
                         s t a t u s = ' o p e n ' ,  
                         a u t o _ a s s i g n _ e n a b l e d = T r u e ,  
                         d o e r _ _ i s n u l l = T r u e  
                 )  
                  
                 p r o c e s s e d _ c o u n t   =   0  
                  
                 f o r   t a s k   i n   c a n d i d a t e _ t a s k s :  
                         #   C h e c k   f o r   a p p l i c a t i o n s  
                         a p p s   =   t a s k . a p p l i c a t i o n s . f i l t e r ( s t a t u s = ' p e n d i n g ' )  
                          
                         i f   a p p s . e x i s t s ( ) :  
                                 #   W e   h a v e   a p p l i c a n t s .   C h e c k   t h e   w i n d o w .  
                                 f i r s t _ a p p   =   t a s k . a p p l i c a t i o n s . o r d e r _ b y ( ' f i r s t _ a p p l i c a t i o n _ t i m e ' ) . f i r s t ( )  
                                 i f   n o t   f i r s t _ a p p . f i r s t _ a p p l i c a t i o n _ t i m e :  
                                         #   S h o u l d   v e r i f y   t h i s   f i e l d   i s   p o p u l a t e d .   I f   n o t ,   f a l l b a c k   t o   c r e a t e d _ a t  
                                         s t a r t _ t i m e   =   f i r s t _ a p p . c r e a t e d _ a t  
                                 e l s e :  
                                         s t a r t _ t i m e   =   f i r s t _ a p p . f i r s t _ a p p l i c a t i o n _ t i m e  
                                  
                                 t i m e _ e l a p s e d   =   n o w   -   s t a r t _ t i m e  
                                  
                                 i f   t i m e _ e l a p s e d   > =   t i m e d e l t a ( m i n u t e s = 3 ) :  
                                         #   W I N D O W   C L O S E D   - >   P I C K   W I N N E R  
                                         l o g g e r . i n f o ( f " â  ³   T a s k   { t a s k . i d }   w i n d o w   c l o s e d .   S e l e c t i n g   b e s t   a p p l i c a n t   f r o m   { a p p s . c o u n t ( ) }   c a n d i d a t e s . " )  
                                          
                                         #   S c o r e   a p p l i c a n t s  
                                         b e s t _ a p p   =   N o n e  
                                         b e s t _ s c o r e   =   - 1  
                                          
                                         f o r   a p p   i n   a p p s :  
                                                 s c o r e   =   a p p . r a n k i n g _ s c o r e  
                                                 i f   s c o r e   >   b e s t _ s c o r e :  
                                                         b e s t _ s c o r e   =   s c o r e  
                                                         b e s t _ a p p   =   a p p  
                                          
                                         i f   b e s t _ a p p :  
                                                 #   A S S I G N !  
                                                 t a s k . d o e r   =   b e s t _ a p p . d o e r  
                                                 t a s k . s t a t u s   =   ' i n _ p r o g r e s s '   #   O r   ' a s s i g n e d '   i f   y o u   h a v e   t h a t   s t a t u s  
                                                 t a s k . s a v e ( )  
                                                  
                                                 #   U p d a t e   a p p l i c a t i o n s  
                                                 b e s t _ a p p . s t a t u s   =   ' a c c e p t e d '  
                                                 b e s t _ a p p . s a v e ( )  
                                                  
                                                 #   R e j e c t   o t h e r s ?   O r   k e e p   a s   b a c k u p ?   U s u a l l y   r e j e c t   o r   k e e p   p e n d i n g .  
                                                 #   L e t ' s   k e e p   p e n d i n g   f o r   n o w   o r   m a r k   r e j e c t e d ?    
                                                 #   R e q u i r e m e n t :   " a l l o c a t e s   e r r a n d s " .   I m p l i e s   s e l e c t i o n .  
                                                  
                                                 #   C r e a t e   A s s i g n m e n t   R e c o r d  
                                                 T a s k A s s i g n m e n t . o b j e c t s . c r e a t e (  
                                                         t a s k = t a s k ,  
                                                         a g e n t = b e s t _ a p p . d o e r ,  
                                                         s t a t u s = ' a c c e p t e d ' ,   #   P r e - a c c e p t e d   s i n c e   t h e y   a p p l i e d  
                                                         a s s i g n m e n t _ m e t h o d = ' a p p l i c a t i o n ' ,  
                                                         t o t a l _ m a t c h _ s c o r e = b e s t _ s c o r e ,  
                                                         a s s i g n m e n t _ n o t e s = f " W i n n e r   o f   3 - m i n u t e   a p p l i c a t i o n   w i n d o w   ( S c o r e :   { b e s t _ s c o r e } ) "  
                                                 )  
                                                  
                                                 #   N o t i f y  
                                                 N o t i f i c a t i o n . o b j e c t s . c r e a t e (  
                                                         u s e r = b e s t _ a p p . d o e r ,  
                                                         t y p e = ' a p p l i c a t i o n _ a c c e p t e d ' ,  
                                                         t i t l e = ' ð x}0   A p p l i c a t i o n   A c c e p t e d ! ' ,  
                                                         m e s s a g e = f ' Y o u   h a v e   b e e n   s e l e c t e d   f o r   " { t a s k . t i t l e } " ! ' ,  
                                                         r e l a t e d _ t a s k = t a s k  
                                                 )  
                                                  
                                                 p r o c e s s e d _ c o u n t   + =   1  
                                                  
                         e l s e :  
                                 #   N O   A P P L I C A N T S  
                                 #   C h e c k   c r e a t i o n   t i m e .   I f   i t ' s   b e e n   o p e n   f o r   a   w h i l e   ( e . g .   1 0   m i n s )   a n d   n o   o n e   a p p l i e d ,  
                                 #   m a y b e   t r i g g e r   " P u s h "   a s s i g n m e n t   i f   u r g e n c y   i s   h i g h ?  
                                 #   F o r   n o w ,   l e t ' s   s t r i c t l y   f o l l o w   " A u t o   A s s i g n "   f l a g   m e a n i n g   " P u s h   i f   n o   o n e   p i c k s   i t   u p " ?  
                                 #   O R ,   m a y b e   a u t o _ a s s i g n _ t a s k   I S   t h e   p u s h   m e c h a n i s m   r e q u e s t e d .  
                                  
                                 #   L e t ' s   s a y   i f   i t ' s   h i g h   p r i o r i t y   a n d   >   1 0   m i n s   o l d ,   t r y   t o   p u s h .  
                                 i f   t a s k . p r i o r i t y _ l e v e l   > =   4   a n d   ( n o w   -   t a s k . c r e a t e d _ a t )   >   t i m e d e l t a ( m i n u t e s = 1 0 ) :  
                                           l o g g e r . i n f o ( f " ð xa¬   H i g h   u r g e n c y   t a s k   { t a s k . i d }   h a s   n o   a p p l i c a n t s .   A t t e m p t i n g   p u s h   a s s i g n m e n t . " )  
                                           #   C h e c k   i f   w e   a l r e a d y   t r i e d   p u s h i n g ?   ( A v o i d   s p a m m i n g )  
                                           #   C h e c k   i f   e x i s t i n g   a s s i g n m e n t s   f a i l e d ?  
                                           #   F o r   s i m p l i c i t y / m v p :   T r y   o n c e .  
                                           #   W e   n e e d   t o   i m p o r t   a u t o _ a s s i g n _ t a s k   f r o m   v i e w s ?   C i r c u l a r   i m p o r t   r i s k .  
                                           #   B e t t e r   t o   m o v e   l o g i c   t o   u t i l s   o r   s e r v i c e s .  
                                           #   F o r   n o w ,   l e t ' s   k e e p   i t   s i m p l e :   J u s t   l o g g i n g   o r   s k i p p i n g   p u s h   t o   a v o i d   c o m p l e x i t y   u n l e s s   e x p l i c i t l y   r e q u e s t e d .  
                                           #   T h e   u s e r   a s k e d   f o r   " a l l o c a t e s   e r r a n d s . . .   b a s e d   o n   c r i t e r i a " .   T h e   W i n n e r   P i c k e r   c o v e r s   t h i s .  
                                           p a s s  
                  
                 i f   p r o c e s s e d _ c o u n t   >   0 :  
                         l o g g e r . i n f o ( f " ð x¤    A u t o - a s s i g n e d   { p r o c e s s e d _ c o u n t }   t a s k s   f r o m   a p p l i c a t i o n   p o o l " )  
                          
                 r e t u r n   { ' s u c c e s s ' :   T r u e ,   ' p r o c e s s e d ' :   p r o c e s s e d _ c o u n t }  
                  
         e x c e p t   E x c e p t i o n   a s   e :  
                 l o g g e r . e r r o r ( f " E r r o r   i n   p r o c e s s _ t a s k _ a s s i g n m e n t s :   { s t r ( e ) } " )  
                 r e t u r n   { ' s u c c e s s ' :   F a l s e ,   ' e r r o r ' :   s t r ( e ) }  
 