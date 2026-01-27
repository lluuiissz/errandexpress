import os
import sys
import django
from django.conf import settings

# Setup Django Environment
sys.path.append(os.path.abspath('errandexpress'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from django.urls import reverse
from django.template.loader import get_template
from core.utils import check_pending_ratings

def check_compatibility():
    print("🔍 System Compatibility Check")
    print("===========================")
    errors = 0

    # 1. Verify Helper Function
    try:
        print(f"✅ 'check_pending_ratings' importable: {check_pending_ratings}")
    except ImportError:
        print("❌ 'check_pending_ratings' missing from core.utils")
        errors += 1

    # 2. Verify URL Configuration
    try:
        url = reverse('pending_ratings')
        print(f"✅ URL 'pending_ratings' resolves to: {url}")
    except Exception as e:
        print(f"❌ URL 'pending_ratings' failed resolution: {e}")
        errors += 1

    # 3. Verify Template Existence
    try:
        tmpl = get_template('pending_ratings.html')
        print(f"✅ Template 'pending_ratings.html' found: {tmpl.template.name}")
    except Exception as e:
        print(f"❌ Template 'pending_ratings.html' missing or invalid: {e}")
        errors += 1
        
    # 4. Verify View Imports (Circular Dependency Check)
    try:
        from core import views
        if hasattr(views, 'pending_ratings'):
            print("✅ View 'pending_ratings' exists in core.views")
        else:
            print("❌ View 'pending_ratings' MISSING in core.views")
            errors += 1
            
        if hasattr(views, 'admin_dashboard'):
             print("✅ View 'admin_dashboard' exists in core.views")
    except Exception as e:
        print(f"❌ Error importing core.views (Circular Import?): {e}")
        errors += 1

    print("\n---------------------------")
    if errors == 0:
        print("🎉 SUCCESS: All updates are compatible and integrated correctly.")
    else:
        print(f"⚠️ FAILURE: Found {errors} compatibility issues.")

if __name__ == "__main__":
    check_compatibility()
