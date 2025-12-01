import os
import sys

# Add Django project to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, '..', 'errandexpress'))

# Configure Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'errandexpress.settings'

# Initialize Django
import django
django.setup()

# Get WSGI application
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
