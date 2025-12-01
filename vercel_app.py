"""
Minimal WSGI handler for Vercel
"""

def application(environ, start_response):
    """
    WSGI application entry point
    """
    import sys
    import os
    
    # Setup paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if os.path.join(BASE_DIR, 'errandexpress') not in sys.path:
        sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
    os.environ.setdefault('DEBUG', 'False')
    
    # Try to get Django WSGI app
    try:
        import django
        if not django.apps.apps.ready:
            django.setup()
        
        from django.core.wsgi import get_wsgi_application
        django_app = get_wsgi_application()
        return django_app(environ, start_response)
        
    except Exception as e:
        import traceback
        error_html = f"""
        <html>
        <head><title>Error</title></head>
        <body style="font-family: monospace; padding: 20px;">
            <h1>Django Initialization Error</h1>
            <pre>{str(e)}</pre>
            <h3>Traceback:</h3>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [error_html.encode('utf-8')]

# Vercel expects these
app = application
handler = application
