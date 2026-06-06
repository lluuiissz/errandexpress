
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Task, Notification
from core.tasks import handle_overdue_tasks

User = get_user_model()

# 1. Setup User
user = User.objects.filter(is_superuser=True).first() or User.objects.first()
if not user:
    print("No user found.")
    exit(1)

print(f"Testing with user: {user.fullname} ({user.email})")

# 2. Create Expired Task
now = timezone.now()
expired_deadline = now - timedelta(hours=1) # 1 hour ago

task = Task.objects.create(
    poster=user,
    title="Test Expired Task (No Doer)",
    description="This task should be marked as expired because the deadline has passed.",
    category="errands",
    price=500,
    payment_method="cod",
    deadline=expired_deadline,
    status="open", # Crucial: Open status means no one assigned/completed
    location="Test Location"
)

print(f"Created expired task: '{task.title}' (ID: {task.id})")
print(f" - Deadline: {task.deadline}")
print(f" - Status: {task.status}")
print(f" - Is Expired? {task.is_expired}")

# 3. specific check: Ensure no notification exists yet
Notification.objects.filter(related_task=task).delete()

# 4. Run Logic
print("\nRunning handle_overdue_tasks()...")
result = handle_overdue_tasks()
print(f"Result: {result}")

# 5. Verify Notification
notif = Notification.objects.filter(
    user=user, 
    related_task=task,
    type='task_expired'
).first()

if notif:
    print("\n✅ SUCCESS: 'task_expired' notification created!")
    print(f" - Title: {notif.title}")
    print(f" - Message: {notif.message}")
else:
    print("\n❌ FAILURE: Notification not found.")

# 6. Verify Standard Overdue (In Progress) Logic doesn't fire
overdue_notif = Notification.objects.filter(
    user=user,
    related_task=task,
    type='task_overdue'
).exists()

if not overdue_notif:
    print("✅ SUCCESS: Standard 'task_overdue' notification was CORRECTLY skipped.")
else:
    print("❌ FAILURE: Standard 'task_overdue' notification was INCORRECTLY sent.")

print(f"\n[Verification] Open this URL to check the Update/Delete buttons:")
print(f"http://127.0.0.1:8000/tasks/{task.id}/")
