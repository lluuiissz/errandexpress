"""
Django WSGI Application for Vercel
Simplified version that always exports a proper WSGI application
"""

import sys
import os

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
os.environ.setdefault('DEBUG', 'False')

# Initialize Django
import django
django.setup()

# Get WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Export for Vercel
app = application
handler = application
