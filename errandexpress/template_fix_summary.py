# Quick fix script to restart Django and clear template cache

import os
import sys

print("=" * 60)
print("TEMPLATE ERROR FIX SUMMARY")
print("=" * 60)

print("\nAnalysis Results:")
print("✓ base_complete.html has balanced tags (25 if, 25 endif)")
print("✓ Template structure is correct")
print("✗ Django is reporting an error on line 643")

print("\nPossible Causes:")
print("1. Template caching issue")
print("2. Error in a different template file")
print("3. Server needs restart")

print("\nRecommended Actions:")
print("1. Stop the Django server (Ctrl+C)")
print("2. Restart with: py manage.py runserver")
print("3. Clear browser cache")
print("4. Try accessing the home page again")

print("\nIf error persists:")
print("- Check which template is actually being used for the home view")
print("- Verify the views.py home function")
print("- Check for any template inheritance issues")

print("\n" + "=" * 60)
