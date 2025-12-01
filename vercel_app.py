import sys
import os
import traceback

try:
    # Add the errandexpress directory to Python path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
    
    # Set environment defaults for Vercel
    os.environ.setdefault('DEBUG', 'False')
    
    # Check critical environment variables
    required_vars = ['DJANGO_SECRET_KEY', 'ALLOWED_HOSTS']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        # Create a simple error response
        def app(environ, start_response):
            error_msg = f"Missing environment variables: {', '.join(missing_vars)}\n\n"
            error_msg += "Please set these in Vercel Dashboard → Settings → Environment Variables:\n"
            error_msg += "- DJANGO_SECRET_KEY\n"
            error_msg += "- DATABASE_URL (optional, defaults to sqlite)\n"
            error_msg += "- ALLOWED_HOSTS (your Vercel domain)\n"
            error_msg += "- DEBUG (set to False)\n"
            
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [error_msg.encode('utf-8')]
    else:
        # Import Django and setup
        import django
        django.setup()
        
        # Import Django WSGI application
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        
        # Vercel expects 'app' or 'handler' variable
        app = application
        handler = application

except Exception as e:
    # Create error handler that shows the actual error
    error_trace = traceback.format_exc()
    
    def app(environ, start_response):
        error_msg = f"Django Initialization Error:\n\n{str(e)}\n\nTraceback:\n{error_trace}"
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [error_msg.encode('utf-8')]
    
    handler = app
