from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Task, Message, Notification

class Command(BaseCommand):
    help = 'Deletes chat messages for tasks that have been expired for over 24 hours'

    def handle(self, *args, **options):
        # Calculate the threshold: 24 hours ago
        threshold_time = timezone.now() - timedelta(hours=24)
        
        # Find tasks where deadline is less than threshold_time (expired > 24h ago)
        # We target open/in_progress tasks mostly, but it acts as a catch-all for any task meeting the condition
        expired_tasks = Task.objects.filter(
            deadline__lt=threshold_time
        )
        
        deleted_conversations = 0
        
        for task in expired_tasks:
            # Check if there are actually messages to delete
            messages = Message.objects.filter(task=task)
            if messages.exists():
                deleted_count, _ = messages.delete()
                
                if deleted_count > 0:
                    deleted_conversations += 1
                    
                    # Notify poster
                    Notification.objects.create(
                        user=task.poster,
                        type='system_message',
                        title='Conversation Expired & Deleted',
                        message=f'The conversation for expired task "{task.title}" has been permanently deleted for privacy due to 24 hours of inactivity past the deadline.',
                        related_task=task
                    )
                    
                    # Notify doer
                    if task.doer:
                        Notification.objects.create(
                            user=task.doer,
                            type='system_message',
                            title='Conversation Expired & Deleted',
                            message=f'The conversation for expired task "{task.title}" has been permanently deleted for privacy due to 24 hours of inactivity past the deadline.',
                            related_task=task
                        )
                        
        self.stdout.write(self.style.SUCCESS(f'Successfully cleared chat histories for {deleted_conversations} expired tasks.'))
