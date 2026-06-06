
import os
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.models import User, Task, Notification
from core.tasks import send_deadline_reminders

def run_test():
    print("🧪 Starting Deadline Notification Logic Test...")
    
    # 1. Setup Test Data
    # Create unique poster name to avoid collisions
    poster_name = f"test_poster_{timezone.now().timestamp()}"
    poster = User.objects.create(username=poster_name, email=f"{poster_name}@test.com", fullname="Test Poster")
    
    doer_name = f"test_doer_{timezone.now().timestamp()}"
    doer = User.objects.create(username=doer_name, email=f"{doer_name}@test.com", fullname="Test Doer")
    
    now = timezone.now()
    
    # Task 1: CRITICAL (Deadline in 10 mins)
    task_critical = Task.objects.create(
        poster=poster,
        doer=doer,
        title="Critical Task",
        description="Testing critical bucket",
        category="microtask",
        price=100,
        payment_method="cod",
        deadline=now + timedelta(minutes=10),
        status="in_progress",
        tags="test"
    )
    
    # Task 2: URGENT (Deadline in 90 mins)
    task_urgent = Task.objects.create(
        poster=poster,
        doer=doer,
        title="Urgent Task",
        description="Testing urgent bucket",
        category="microtask",
        price=100,
        payment_method="cod",
        deadline=now + timedelta(minutes=90),
        status="in_progress",
        tags="test"
    )
    
    # Task 3: STANDARD (Deadline in 23 hours)
    task_standard = Task.objects.create(
        poster=poster,
        doer=doer,
        title="Standard Task",
        description="Testing standard bucket",
        category="microtask",
        price=100,
        payment_method="cod",
        deadline=now + timedelta(hours=23),
        status="in_progress",
        tags="test"
    )
    
    print("✅ Test tasks created.")
    
    # 2. Run Logic First Time
    print("🔄 Running send_deadline_reminders() [Run 1]...")
    result = send_deadline_reminders()
    print(f"   Result: {result}")
    
    # Verify Notifications
    # Both Poster and Doer should get notifications for ALL 3 tasks 
    # (Because they fall into the buckets: <20m, <2h, <24h)
    
    # Check Critical
    notif_critical = Notification.objects.filter(related_task=task_critical, type='deadline_reminder').count()
    if notif_critical == 2: # 1 for poster, 1 for doer
        print("   ✅ Critical Task: Correctly sent 2 notifications.")
    else:
        print(f"   ❌ Critical Task: Expected 2 notifications, got {notif_critical}.")

    # Check Urgent
    notif_urgent = Notification.objects.filter(related_task=task_urgent, type='deadline_reminder').count()
    if notif_urgent == 2:
        print("   ✅ Urgent Task: Correctly sent 2 notifications.")
    else:
        print(f"   ❌ Urgent Task: Expected 2 notifications, got {notif_urgent}.")
        
    # Check Standard
    notif_standard = Notification.objects.filter(related_task=task_standard, type='deadline_reminder').count()
    if notif_standard == 2:
        print("   ✅ Standard Task: Correctly sent 2 notifications.")
    else:
        print(f"   ❌ Standard Task: Expected 2 notifications, got {notif_standard}.")
        
        
    # 3. Run Logic Second Time (Immediately)
    # SHOULD NOT SEND ANY NEW NOTIFICATIONS because of throttling (2m, 20m, 24h)
    print("🔄 Running send_deadline_reminders() [Run 2 - Throttled]...")
    result_2 = send_deadline_reminders()
    print(f"   Result: {result_2}")
    
    if result_2['reminders_sent'] == 0:
        print("   ✅ Throttling Check: 0 new reminders sent (Correct).")
    else:
        print(f"   ❌ Throttling Check: Sent {result_2['reminders_sent']} reminders (Expected 0).")
        
    # Cleanup
    poster.delete()
    doer.delete() # Cascade deletes tasks/notifs
    print("🧹 Cleanup complete.")

if __name__ == '__main__':
    run_test()
