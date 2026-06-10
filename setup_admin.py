
import os
import django
import sys

# Add project root to sys.path
sys.path.append(r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.models import User

# Check for existing admin
admin = User.objects.filter(email='admin@errandexpress.com').first()
if not admin:
    print("Creating admin user...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@errandexpress.com',
        password='password123',
        fullname='System Admin',
        role='admin'
    )
else:
    print("Admin user exists. resetting password...")
    admin.set_password('password123')
    admin.role = 'admin'
    admin.save()

print(f"Admin Ready: {admin.email} / password123")
