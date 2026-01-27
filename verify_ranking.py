import os
import sys
import django
from django.db.models import Avg, Count, Q, F, Value, DecimalField, OuterRef, Subquery, Prefetch
from django.db.models.functions import Coalesce

# Setup Django
sys.path.append(os.path.abspath('errandexpress'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.models import User, Task, TaskApplication, Rating

def verify_ranking():
    print("🔍 Ranking Algorithm Verification")
    print("================================")
    
    # 1. Inspect the logic effectively by simulating it
    # We will look at existing users/apps or mocked logic
    
    # Let's query actual applications for a task if one exists
    task = Task.objects.filter(applications__isnull=False).first()
    
    if not task:
        print("❌ No tasks with applications found. Cannot verify with real data.")
        return

    print(f"Checking Task: {task.title} (ID: {task.id})")
    
    # Replicate the View Logic exactly
    applications = TaskApplication.objects.filter(
        task=task
    ).select_related('doer')
    
    # Calculate real-time ratings (Same as View)
    doer_rating_subquery = Rating.objects.filter(
        rated=OuterRef('doer')
    ).values('rated').annotate(
        avg_rating=Avg('score')
    ).values('avg_rating')
    
    applications = applications.annotate(
        doer_current_rating=Coalesce(
            Subquery(doer_rating_subquery, output_field=DecimalField(max_digits=3, decimal_places=2)),
            Value(0.0, output_field=DecimalField(max_digits=3, decimal_places=2)),
            output_field=DecimalField(max_digits=3, decimal_places=2)
        ),
        doer_completed_count=Count(
            'doer__assigned_tasks',
            filter=Q(doer__assigned_tasks__status='completed')
        )
    )
    
    print("\nApplicant Scores:")
    print("-" * 60)
    print(f"{'User':<20} | {'Rating':<6} | {'Tasks':<5} | {'Newbie?':<7} | {'SCORE':<5}")
    print("-" * 60)
    
    app_list = list(applications)
    for app in app_list:
        # Replicate python calculation from view
        rating = float(app.doer_current_rating)
        completed = app.doer_completed_count
        is_newbie = completed < 3
        
        score = (rating * 10) + (completed * 2) + (15 if is_newbie else 0)
        
        # Determine strict sorting value
        app.calculated_score = score
        
        print(f"{app.doer.fullname[:20]:<20} | {rating:<6.2f} | {completed:<5} | {str(is_newbie):<7} | {score:<5.1f}")

    print("-" * 60)
    
    # Sort and Check
    sorted_apps = sorted(app_list, key=lambda x: x.calculated_score, reverse=True)
    
    print("\nSorted Order (Highest First):")
    for i, app in enumerate(sorted_apps, 1):
        print(f"{i}. {app.doer.fullname} (Score: {app.calculated_score})")
        
    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    verify_ranking()
