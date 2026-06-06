import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "errandexpress.settings")
django.setup()

from core.models import Task

print("Testing tag auto-population...")

# Get any existing task or just create a mock instance in memory (or use a real one from DB)
t = Task.objects.first()
if t:
    print(f"Original Category: {t.category}")
    print(f"Original Tags: {t.tags}")
    
    # Change to typing
    t.category = 'typing'
    t.save()
    print(f"After changing to 'typing': {t.tags}")
    
    # Change to powerpoint
    t.category = 'powerpoint'
    t.save()
    print(f"After changing to 'powerpoint': {t.tags}")
else:
    print("No tasks found to test.")
