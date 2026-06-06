import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "errandexpress.settings")
django.setup()

from core.models import Task, User, StudentSkill
from django.utils import timezone

print("=== RECENT TASKS ===")
for t in Task.objects.all().order_by('-updated_at')[:5]:
    print(f"Task ID: {t.id}")
    print(f"Title: {t.title}")
    print(f"Category: {t.category}")
    print(f"Tags: {t.tags}")
    print(f"Poster: {t.poster.username}")
    print(f"Status: {t.status}")
    print("---")

print("\n=== DOERS AND SKILLS ===")
doers = User.objects.filter(role='task_doer')[:3]
for d in doers:
    skills = StudentSkill.objects.filter(student=d, status='verified').values_list('skill_name', flat=True)
    print(f"Doer: {d.username}, Skills: {list(skills)}")
