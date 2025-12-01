import sys
import os

# Add the errandexpress directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'errandexpress'))

# Import Django WSGI application
from errandexpress.wsgi import application

# Vercel expects 'app' variable
app = application
