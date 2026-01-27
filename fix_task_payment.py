import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.abspath('errandexpress'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.models import Task

def fix_payment_amount():
    task_id = "7a1f4ce2-a000-4aef-ab2a-caed199946a6"
    try:
        task = Task.objects.get(id=task_id)
        print(f"Task found: {task.title}")
        print(f"Current Price: {task.price}")
        print(f"Current Doer Payment: {task.doer_payment_amount}")
        
        # apply fix: doer gets 100% of price
        task.doer_payment_amount = task.price
        task.save()
        
        print(f"✅ UPDATED Doer Payment to: {task.doer_payment_amount}")
        
    except Task.DoesNotExist:
        print(f"❌ Task {task_id} not found.")

if __name__ == "__main__":
    fix_payment_amount()
