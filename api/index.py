from django.core.wsgi import get_wsgi_application
import os
import sys

# Add errandexpress to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'errandexpress'))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
os.environ.setdefault('DEBUG', 'False')

# Initialize Django
import django
django.setup()

# Get application
app = get_wsgi_application()
