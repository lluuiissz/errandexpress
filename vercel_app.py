import sys
import os

# Add the errandexpress directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')

# Import Django and setup
import django
django.setup()

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel expects 'app' or 'handler' variable
app = application
handler = application
