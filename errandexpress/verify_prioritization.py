"""
Script to verify prioritization service implementation
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.services import PrioritizationService
from core.models import Task, User
from django.utils import timezone

print("=" * 80)
print("PRIORITIZATION SERVICE VERIFICATION")
print("=" * 80)

# Test 1: Check if service exists
print("\n✓ Test 1: PrioritizationService class exists")
print(f"  Service class: {PrioritizationService}")

# Test 2: Check scoring methods
print("\n✓ Test 2: Scoring methods exist")
methods = [
    'calculate_urgency_score',
    'calculate_location_score',
    'calculate_preference_score',
    'calculate_time_window_score',
    'calculate_price_score',
    'calculate_deadline_urgency_score',
    'get_prioritized_tasks',
    'get_score_breakdown'
]
for method in methods:
    if hasattr(PrioritizationService, method):
        print(f"  ✅ {method}")
    else:
        print(f"  ❌ {method} - MISSING!")

# Test 3: Check scoring weights
print("\n✓ Test 3: Scoring weights defined")
weights = {
    'URGENCY_WEIGHT': PrioritizationService.URGENCY_WEIGHT,
    'LOCATION_WEIGHT': PrioritizationService.LOCATION_WEIGHT,
    'PREFERENCE_WEIGHT': PrioritizationService.PREFERENCE_WEIGHT,
    'TIME_WINDOW_WEIGHT': PrioritizationService.TIME_WINDOW_WEIGHT,
    'PRICE_WEIGHT': PrioritizationService.PRICE_WEIGHT,
    'RATING_WEIGHT': PrioritizationService.RATING_WEIGHT,
    'DEADLINE_WEIGHT': PrioritizationService.DEADLINE_WEIGHT,
}
for name, value in weights.items():
    print(f"  {name}: {value}")

# Test 4: Calculate max possible score
print("\n✓ Test 4: Maximum possible score")
max_score = sum(weights.values())
print(f"  Max Score: {max_score}")

# Test 5: Test with real data (if available)
print("\n✓ Test 5: Test with database")
task_count = Task.objects.count()
user_count = User.objects.filter(role='task_doer').count()
print(f"  Total tasks: {task_count}")
print(f"  Total doers: {user_count}")

if task_count > 0 and user_count > 0:
    # Get a sample task and user
    sample_task = Task.objects.first()
    sample_user = User.objects.filter(role='task_doer').first()
    
    print(f"\n  Sample Task: {sample_task.title}")
    print(f"  Sample User: {sample_user.fullname}")
    
    # Get score breakdown
    try:
        breakdown = PrioritizationService.get_score_breakdown(sample_task, sample_user)
        print("\n  Score Breakdown:")
        for key, value in breakdown.items():
            print(f"    {key}: {value}")
    except Exception as e:
        print(f"  ⚠️  Error calculating breakdown: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
