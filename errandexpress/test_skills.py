import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "errandexpress.settings")
django.setup()

from core.models import User, StudentSkill

verified_skills = StudentSkill.objects.filter(status='verified')
for s in verified_skills:
    print(f"User: {s.student.username}, Skill: {s.skill_name}")

if not verified_skills:
    print("NO VERIFIED SKILLS IN DATABASE")
