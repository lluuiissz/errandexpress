
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Task, Notification
from core.tasks import auto_delete_expired_tasks

User = get_user_model()
user = User.objects.filter(is_superuser=True).first()

print(f"Testing with user: {user.username}")

# 1. Create a task eligible for auto-deletion
# Condition: Open + Deadline < Now - 24h
now = timezone.now()
eligible_deadline = now - timedelta(hours=25) 
not_eligible_deadline = now - timedelta(hours=23)

t1 = Task.objects.create(
    poster=user,
    title="Should Be Deleted",
    category="errands",
    price=100,
    payment_method="cod",
    deadline=eligible_deadline,
    status="open"
)

t2 = Task.objects.create(
    poster=user,
    title="Should NOT Be Deleted (Grace Period)",
    category="errands",
    price=100,
    payment_method="cod",
    deadline=not_eligible_deadline,
    status="open"
)

print(f"Created Task 1 (Eligible): {t1.title} | Deadline: {t1.deadline}")
print(f"Created Task 2 (Safe): {t2.title} | Deadline: {t2.deadline}")

# 2. Run the task
print("\nRunning auto_delete_expired_tasks()...")
result = auto_delete_expired_tasks()
print(f"Result: {result}")

# 3. Verify Logic
# T1 should be deleted
if not Task.objects.filter(id=t1.id).exists():
    print("✅ SUCCESS: Task 1 was deleted.")
else:
    print("❌ FAILURE: Task 1 remains.")

# T2 should exist
if Task.objects.filter(id=t2.id).exists():
    print("✅ SUCCESS: Task 2 was preserved (Grace period active).")
else:
    print("❌ FAILURE: Task 2 was incorrectly deleted.")

# 4. Verify Notification
notif = Notification.objects.filter(
    user=user,
    title="🗑️ Task Auto-Deleted"
).last()

if notif:
    print(f"✅ SUCCESS: Notification sent: '{notif.message}'")
else:
    print("❌ FAILURE: No deletion notification found.")

# Cleanup
if Task.objects.filter(id=t2.id).exists():
    t2.delete()
