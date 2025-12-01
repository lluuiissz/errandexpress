"""
Minimal Vercel handler for Django
This version includes extensive error handling and diagnostics
"""

def app(environ, start_response):
    """WSGI application callable"""
    import sys
    import os
    
    try:
        # Step 1: Setup paths
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(BASE_DIR, 'errandexpress'))
        
        # Step 2: Check environment variables
        env_status = []
        env_status.append(f"DJANGO_SECRET_KEY: {'SET' if os.environ.get('DJANGO_SECRET_KEY') else 'MISSING'}")
        env_status.append(f"ALLOWED_HOSTS: {os.environ.get('ALLOWED_HOSTS', 'MISSING')}")
        env_status.append(f"DEBUG: {os.environ.get('DEBUG', 'MISSING')}")
        env_status.append(f"DATABASE_URL: {'SET' if os.environ.get('DATABASE_URL') else 'MISSING'}")
        
        # Step 3: Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
        os.environ.setdefault('DEBUG', 'False')
        
        # Step 4: Try to import Django
        try:
            import django
            django_version = django.get_version()
            env_status.append(f"Django version: {django_version}")
        except ImportError as e:
            env_status.append(f"Django import failed: {str(e)}")
            raise
        
        # Step 5: Setup Django
        try:
            django.setup()
            env_status.append("Django setup: SUCCESS")
        except Exception as e:
            env_status.append(f"Django setup failed: {str(e)}")
            raise
        
        # Step 6: Get WSGI application
        try:
            from django.core.wsgi import get_wsgi_application
            django_app = get_wsgi_application()
            env_status.append("WSGI app created: SUCCESS")
            
            # Call the Django app
            return django_app(environ, start_response)
            
        except Exception as e:
            env_status.append(f"WSGI app creation failed: {str(e)}")
            raise
            
    except Exception as e:
        # Return detailed error information
        import traceback
        error_html = f"""
        <html>
        <head><title>Django Initialization Error</title></head>
        <body style="font-family: monospace; padding: 20px;">
            <h1>Django Initialization Error</h1>
            <h2>Error: {str(e)}</h2>
            <h3>Environment Status:</h3>
            <pre>{'<br>'.join(env_status)}</pre>
            <h3>Python Path:</h3>
            <pre>{sys.path}</pre>
            <h3>Traceback:</h3>
            <pre>{traceback.format_exc()}</pre>
            <h3>Environment Variables:</h3>
            <pre>{chr(10).join([f"{k}: {v[:20]}..." if len(str(v)) > 20 else f"{k}: {v}" for k, v in sorted(os.environ.items()) if not k.startswith('_')])}</pre>
        </body>
        </html>
        """
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [error_html.encode('utf-8')]

# Vercel expects these
handler = app
