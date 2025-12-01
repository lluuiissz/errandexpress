"""
Django WSGI Application for Vercel
Module-level initialization for serverless deployment
"""

import sys
import os

# Setup paths - runs ONCE when module loads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')

# Set production defaults
os.environ.setdefault('DEBUG', 'False')

# Initialize Django - runs ONCE
import django
django.setup()

# Create WSGI application - runs ONCE
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Export for Vercel (module-level variables)
app = application
handler = application
