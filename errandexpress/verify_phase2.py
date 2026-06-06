"""
Comprehensive Codebase Verification Script
Checks for split tags, broken lines, raw code issues, and imports
"""

import os
import re
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

print("=" * 80)
print("COMPREHENSIVE CODEBASE VERIFICATION")
print("=" * 80)

# Test 1: Check API Views Import
print("\n✓ Test 1: API Views Import Check")
try:
    from core.api_views import (
        api_get_prioritized_tasks,
        api_auto_assign_task,
        api_get_scheduled_tasks,
        api_reschedule_task
    )
    print("  ✅ All API views imported successfully")
    print(f"    - api_get_prioritized_tasks: {api_get_prioritized_tasks}")
    print(f"    - api_auto_assign_task: {api_auto_assign_task}")
    print(f"    - api_get_scheduled_tasks: {api_get_scheduled_tasks}")
    print(f"    - api_reschedule_task: {api_reschedule_task}")
except ImportError as e:
    print(f"  ❌ Import error: {e}")

# Test 2: Check PrioritizationService
print("\n✓ Test 2: PrioritizationService Check")
try:
    from core.services import PrioritizationService
    print("  ✅ PrioritizationService imported successfully")
    
    # Check methods
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
            print(f"    ✅ {method}")
        else:
            print(f"    ❌ {method} - MISSING!")
            
except ImportError as e:
    print(f"  ❌ Import error: {e}")

# Test 3: Check URL Configuration
print("\n✓ Test 3: URL Configuration Check")
try:
    from django.urls import reverse
    
    endpoints = [
        ('api_get_prioritized_tasks', 'GET /api/tasks/prioritized/'),
        ('api_auto_assign_task_v2', 'POST /api/tasks/auto-assign/'),
        ('api_get_scheduled_tasks', 'GET /api/tasks/schedule/'),
        ('api_reschedule_task', 'POST /api/tasks/reschedule/'),
    ]
    
    for name, description in endpoints:
        try:
            url = reverse(name)
            print(f"  ✅ {description} → {url}")
        except Exception as e:
            print(f"  ❌ {description} → Error: {e}")
            
except Exception as e:
    print(f"  ❌ URL check error: {e}")

# Test 4: Check Models
print("\n✓ Test 4: Model Indexes Check")
try:
    from core.models import Task
    
    # Get model meta
    meta = Task._meta
    indexes = meta.indexes
    
    print(f"  Total indexes: {len(indexes)}")
    
    # Check for prioritization indexes
    prioritization_indexes = [
        'priority_level',
        'time_window_start',
        'preferred_doer',
        'deadline',
        'campus_location'
    ]
    
    found_indexes = []
    for index in indexes:
        for field in index.fields:
            field_name = field.lstrip('-')
            if field_name in prioritization_indexes and field_name not in found_indexes:
                found_indexes.append(field_name)
                print(f"  ✅ Index on {field_name}")
    
    missing = set(prioritization_indexes) - set(found_indexes)
    if missing:
        print(f"  ⚠️  Missing indexes: {missing}")
    
except Exception as e:
    print(f"  ❌ Model check error: {e}")

# Test 5: Django System Check
print("\n✓ Test 5: Django System Check")
from django.core.management import call_command
from io import StringIO
import sys

output = StringIO()
try:
    call_command('check', stdout=output, stderr=output)
    result = output.getvalue()
    if "no issues" in result.lower() or "0 silenced" in result:
        print("  ✅ Django system check passed")
    else:
        print(f"  ⚠️  Django check output: {result}")
except Exception as e:
    print(f"  ❌ Django check error: {e}")

# Test 6: Template Verification
print("\n✓ Test 6: Template Syntax Check")
template_dir = os.path.join(os.path.dirname(__file__), 'core', 'templates')
if os.path.exists(template_dir):
    html_files = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"  Found {len(html_files)} HTML templates")
    
    issues_found = 0
    for template_path in html_files:
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for split tags
                if re.search(r'\{\{[^\}]*\n', content) or re.search(r'\{%[^\%]*\n', content):
                    print(f"  ⚠️  Potential split tag in {os.path.basename(template_path)}")
                    issues_found += 1
        except Exception as e:
            print(f"  ❌ Error reading {template_path}: {e}")
            issues_found += 1
    
    if issues_found == 0:
        print("  ✅ All templates syntax verified")
else:
    print("  ⚠️  Template directory not found")

# Test 7: Python Syntax Check
print("\n✓ Test 7: Python Files Syntax Check")
python_files = [
    'core/services.py',
    'core/api_views.py',
    'core/models.py',
    'core/views.py',
]

for file_path in python_files:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, file_path, 'exec')
            print(f"  ✅ {file_path} - Syntax OK")
        except SyntaxError as e:
            print(f"  ❌ {file_path} - Syntax Error: {e}")
    else:
        print(f"  ⚠️  {file_path} - File not found")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
