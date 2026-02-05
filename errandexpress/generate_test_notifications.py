
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Notification

User = get_user_model()

# Get the first superuser or first user
user = User.objects.filter(is_superuser=True).first() or User.objects.first()

if not user:
    print("No user found!")
    exit(1)

print(f"Generating test notifications for: {user.username} ({user.fullname})")

# Custom Title for Visibility
deadline_title = "Upcoming Deadline: Grocery Run"
overdue_title = "OVERDUE: Math Tutor Session"

# Create Deadline Reminder (Clock Icon)
Notification.objects.create(
    user=user,
    type='deadline_reminder',
    title=deadline_title,
    message="This task is due in less than 2 hours. Please ensure it is completed on time."
)
print(f" [x] Created 'deadline_reminder' notification: {deadline_title}")

# Create Task Overdue (Warning Triangle)
Notification.objects.create(
    user=user,
    type='task_overdue',
    title=overdue_title,
    message="CRITICAL: This task is now overdue. Please contact support or the other party immediately."
)
print(f" [x] Created 'task_overdue' notification: {overdue_title}")

print("\nDone! Refresh your dashboard to see the icons.")
