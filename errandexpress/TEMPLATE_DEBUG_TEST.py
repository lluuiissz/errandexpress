"""
Template Debug Test Script
Run this to verify what Django is actually rendering
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from django.template.loader import get_template
from django.conf import settings

print("=" * 80)
print("DJANGO TEMPLATE DEBUG TEST")
print("=" * 80)

# Check template directories
print("\n1. TEMPLATE DIRECTORIES:")
for template_config in settings.TEMPLATES:
    print(f"   DIRS: {template_config['DIRS']}")
    print(f"   APP_DIRS: {template_config['APP_DIRS']}")

# Try to load the template
print("\n2. LOADING TEMPLATE: 'browse_tasks_modern.html'")
try:
    template = get_template('browse_tasks_modern.html')
    print(f"   ✅ Template loaded successfully")
    print(f"   Template origin: {template.origin.name if hasattr(template, 'origin') else 'Unknown'}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Check if template has the correct block
print("\n3. CHECKING TEMPLATE CONTENT:")
template_path = os.path.join(settings.BASE_DIR, 'core', 'templates', 'browse_tasks_modern.html')
print(f"   Template path: {template_path}")
print(f"   File exists: {os.path.exists(template_path)}")

if os.path.exists(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for key markers
    checks = {
        'Template Version 3.0': 'Template Version 3.0' in content,
        'extra_scripts block': '{% block extra_scripts %}' in content,
        'window.applyToTask': 'window.applyToTask' in content,
        'window.viewTaskDetail': 'window.viewTaskDetail' in content,
        'lucide.createIcons': 'lucide.createIcons()' in content,
    }
    
    print("\n   Content checks:")
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}: {result}")

# Check base template
print("\n4. CHECKING BASE TEMPLATE:")
base_path = os.path.join(settings.BASE_DIR, 'core', 'templates', 'base_complete.html')
print(f"   Base path: {base_path}")
print(f"   File exists: {os.path.exists(base_path)}")

if os.path.exists(base_path):
    with open(base_path, 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    base_checks = {
        'extra_scripts block defined': '{% block extra_scripts %}' in base_content,
        'Lucide script loaded': 'unpkg.com/lucide' in base_content,
    }
    
    print("\n   Base template checks:")
    for check_name, result in base_checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}: {result}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
