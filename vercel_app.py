"""
Django WSGI Application for Vercel
Module-level initialization for serverless deployment
WITH ERROR HANDLING AND DIAGNOSTICS
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

# Check for required environment variables
required_vars = {
    'DJANGO_SECRET_KEY': os.environ.get('DJANGO_SECRET_KEY'),
    'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS'),
}

missing_vars = [k for k, v in required_vars.items() if not v]

if missing_vars:
    # Create error handler for missing environment variables
    def app(environ, start_response):
        error_html = f"""
        <html>
        <head><title>Environment Variables Missing</title></head>
        <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
            <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h1 style="color: #e74c3c;">⚠️ Environment Variables Not Set</h1>
                <p style="font-size: 16px;">The following required environment variables are missing:</p>
                <ul style="font-size: 14px; color: #c0392b;">
                    {''.join([f'<li><strong>{var}</strong></li>' for var in missing_vars])}
                </ul>
                <hr style="margin: 30px 0;">
                <h2>How to Fix:</h2>
                <ol style="line-height: 1.8;">
                    <li>Go to <a href="https://vercel.com/dashboard">Vercel Dashboard</a></li>
                    <li>Click on your project</li>
                    <li>Go to <strong>Settings</strong> → <strong>Environment Variables</strong></li>
                    <li>Add the following variables:</li>
                </ol>
                <div style="background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 4px; margin: 20px 0;">
                    <pre style="margin: 0;">DJANGO_SECRET_KEY = (u-a=4n#($(jtcmlk*$-2235n&k-_^o1ivcz2()6yhgypx7@0s
ALLOWED_HOSTS = .vercel.app
DEBUG = False
DATABASE_URL = sqlite:///db.sqlite3</pre>
                </div>
                <p style="margin-top: 20px;">
                    <strong>Important:</strong> Check all 3 environment boxes (Production, Preview, Development) for each variable.
                </p>
                <p style="margin-top: 20px;">
                    After adding variables, go to <strong>Deployments</strong> → Click <strong>"Redeploy"</strong>
                </p>
                <hr style="margin: 30px 0;">
                <h3>Current Environment Status:</h3>
                <pre style="background: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto;">
DJANGO_SECRET_KEY: {'✅ SET' if required_vars['DJANGO_SECRET_KEY'] else '❌ MISSING'}
ALLOWED_HOSTS: {'✅ SET (' + required_vars['ALLOWED_HOSTS'] + ')' if required_vars['ALLOWED_HOSTS'] else '❌ MISSING'}
DEBUG: {os.environ.get('DEBUG', 'Not set (defaulting to False)')}
DATABASE_URL: {'✅ SET' if os.environ.get('DATABASE_URL') else '⚠️ Not set (will use SQLite default)'}
                </pre>
            </div>
        </body>
        </html>
        """
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [error_html.encode('utf-8')]
    
    handler = app
else:
    # All required variables present, initialize Django
    try:
        import django
        django.setup()
        
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        
        # Export for Vercel
        app = application
        handler = application
        
    except Exception as e:
        # Django initialization failed
        import traceback
        
        def app(environ, start_response):
            error_html = f"""
            <html>
            <head><title>Django Initialization Error</title></head>
            <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h1 style="color: #e74c3c;">❌ Django Failed to Initialize</h1>
                    <h2>Error:</h2>
                    <pre style="background: #ffe6e6; padding: 15px; border-radius: 4px; color: #c0392b; overflow-x: auto;">{str(e)}</pre>
                    <h3>Full Traceback:</h3>
                    <pre style="background: #ecf0f1; padding: 15px; border-radius: 4px; font-size: 12px; overflow-x: auto;">{traceback.format_exc()}</pre>
                    <h3>Python Path:</h3>
                    <pre style="background: #ecf0f1; padding: 15px; border-radius: 4px; font-size: 12px; overflow-x: auto;">{chr(10).join(sys.path)}</pre>
                </div>
            </body>
            </html>
            """
            start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
            return [error_html.encode('utf-8')]
        
        handler = app
