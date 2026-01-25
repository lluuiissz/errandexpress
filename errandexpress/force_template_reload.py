"""
Force Django to reload templates by clearing the cached template loader
"""

import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')

import django
django.setup()

from django.template import engines
from django.template.loaders import cached

print("=" * 70)
print("CLEARING DJANGO TEMPLATE CACHE")
print("=" * 70)

# Get the Django template engine
django_engine = engines['django']

# Clear the template cache
for template_loader in django_engine.engine.template_loaders:
    if isinstance(template_loader, cached.Loader):
        template_loader.reset()
        print("✓ Cleared cached template loader")

print("\n✓ Template cache cleared successfully!")
print("\nNow restart the Django server:")
print("  1. Stop the server (Ctrl+C)")
print("  2. Run: py manage.py runserver")
print("=" * 70)
