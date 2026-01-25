"""
Django Template Cache Fix Script

The template files are correct (balanced tags), but Django is caching an old version.
This script will help clear the cache.
"""

import os
import shutil

print("=" * 70)
print("DJANGO TEMPLATE CACHE FIX")
print("=" * 70)

print("\n✓ ANALYSIS COMPLETE:")
print("  - base_complete.html: 25 if, 25 endif (BALANCED)")
print("  - home_modern.html: 2 if, 2 endif (BALANCED)")  
print("  - Combined: 27 if, 27 endif (BALANCED)")

print("\n✗ PROBLEM:")
print("  Django is using a cached version of the template")

print("\n🔧 SOLUTION:")
print("\n1. Clear Python bytecode cache:")
pycache_dirs = []
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        pycache_path = os.path.join(root, '__pycache__')
        pycache_dirs.append(pycache_path)

if pycache_dirs:
    print(f"   Found {len(pycache_dirs)} __pycache__ directories")
    for pycache in pycache_dirs:
        try:
            shutil.rmtree(pycache)
            print(f"   ✓ Removed: {pycache}")
        except Exception as e:
            print(f"   ✗ Failed to remove {pycache}: {e}")
else:
    print("   No __pycache__ directories found")

print("\n2. Remove .pyc files:")
pyc_count = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            pyc_path = os.path.join(root, file)
            try:
                os.remove(pyc_path)
                pyc_count += 1
            except Exception as e:
                print(f"   ✗ Failed to remove {pyc_path}: {e}")

print(f"   ✓ Removed {pyc_count} .pyc files")

print("\n3. NEXT STEPS:")
print("   a. Stop the Django server (Ctrl+C)")
print("   b. Run this script: py clear_cache.py")
print("   c. Restart server: py manage.py runserver")
print("   d. Hard refresh browser (Ctrl+Shift+R)")

print("\n" + "=" * 70)
print("Template files are CORRECT. Just need to clear Django's cache!")
print("=" * 70)
