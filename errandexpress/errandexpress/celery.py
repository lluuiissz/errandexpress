"""
Celery configuration for ErrandExpress
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')

app = Celery('errandexpress')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule (periodic tasks)
app.conf.beat_schedule = {
    'send-deadline-reminders': {
        'task': 'core.tasks.send_deadline_reminders',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes for granular warnings
    },
    'auto-delete-expired-tasks': {
        'task': 'core.tasks.auto_delete_expired_tasks',
        'schedule': crontab(minute=0),  # Every hour
    },
    'handle-overdue-tasks': {
        'task': 'core.tasks.handle_overdue_tasks',
        'schedule': crontab(minute=0),  # Every hour
    },
    'retry-failed-payments': {
        'task': 'core.tasks.retry_failed_payments',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'reconcile-pending-payments': {
        'task': 'core.tasks.reconcile_pending_payments',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'cleanup-old-notifications': {
        'task': 'core.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
