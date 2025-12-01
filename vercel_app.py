"""
Django WSGI Application for Vercel
With error handling that always returns a valid WSGI application
"""

import sys
import os

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
os.environ.setdefault('DEBUG', 'False')

# Try to initialize Django
try:
    import django
    django.setup()
    
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
except Exception as e:
    # If Django fails, create a simple WSGI app that shows the error
    import traceback
    
    error_message = f"""
    <html>
    <head><title>Django Initialization Failed</title></head>
    <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
        <div style="background: white; padding: 30px; border-radius: 8px;">
            <h1 style="color: #e74c3c;">Django Failed to Initialize</h1>
            <h2>Error:</h2>
            <pre style="background: #ffe6e6; padding: 15px; border-radius: 4px;">{str(e)}</pre>
            <h3>Traceback:</h3>
            <pre style="background: #ecf0f1; padding: 15px; border-radius: 4px; font-size: 12px; overflow-x: auto;">{traceback.format_exc()}</pre>
        </div>
    </body>
    </html>
    """
    
    def application(environ, start_response):
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [error_message.encode('utf-8')]

# Export for Vercel
app = application
handler = application
