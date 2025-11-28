#!/usr/bin/env python3
"""
Vercel Environment Variables Setup Script

This script helps you set up environment variables for Vercel deployment.
Run this script to generate and configure all required environment variables.
"""

import os
import sys
import json
from pathlib import Path

def generate_django_secret_key():
    """Generate a new Django secret key"""
    from django.core.management.utils import get_random_secret_key
    return get_random_secret_key()

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_section(text):
    """Print a formatted section"""
    print(f"\n>>> {text}\n")

def main():
    print_header("Vercel Environment Variables Setup")
    
    print("""
This script will help you set up environment variables for Vercel deployment.

You have two options:
1. Generate a new Django secret key
2. Use your existing configuration

Let's get started!
    """)
    
    # Step 1: Django Secret Key
    print_section("Step 1: Django Secret Key")
    print("Your current Django secret key (from settings.py):")
    print("  django-insecure-jg*nd55wqq-e!h!&@!$h4oz&)u9d^^9$xyneq#cdmug^lc+x^4")
    print("\nWould you like to generate a NEW secret key? (y/n)")
    
    choice = input("Enter choice (y/n): ").strip().lower()
    if choice == 'y':
        try:
            secret_key = generate_django_secret_key()
            print(f"\n✅ Generated new Django secret key:")
            print(f"   {secret_key}")
        except Exception as e:
            print(f"\n❌ Error generating secret key: {e}")
            print("   Using default key from settings.py")
            secret_key = "django-insecure-jg*nd55wqq-e!h!&@!$h4oz&)u9d^^9$xyneq#cdmug^lc+x^4"
    else:
        secret_key = "django-insecure-jg*nd55wqq-e!h!&@!$h4oz&)u9d^^9$xyneq#cdmug^lc+x^4"
        print(f"\n✅ Using existing Django secret key")
    
    # Step 2: Database URL
    print_section("Step 2: Database URL")
    print("Enter your PostgreSQL connection string (DATABASE_URL):")
    print("Format: postgresql://username:password@host:port/database")
    database_url = input("Enter DATABASE_URL: ").strip()
    
    if not database_url:
        print("❌ Database URL is required!")
        return
    
    # Step 3: Allowed Hosts
    print_section("Step 3: Allowed Hosts")
    print("Enter your allowed hosts (comma-separated):")
    print("Example: errandexpress.vercel.app,localhost,127.0.0.1")
    allowed_hosts = input("Enter ALLOWED_HOSTS: ").strip()
    
    if not allowed_hosts:
        allowed_hosts = "errandexpress.vercel.app,localhost,127.0.0.1"
        print(f"Using default: {allowed_hosts}")
    
    # Step 4: PayMongo Keys
    print_section("Step 4: PayMongo Configuration")
    print("Enter your PayMongo API keys (from PayMongo dashboard):")
    
    paymongo_secret = input("Enter PAYMONGO_SECRET_KEY (or press Enter to skip): ").strip()
    paymongo_public = input("Enter PAYMONGO_PUBLIC_KEY (or press Enter to skip): ").strip()
    paymongo_webhook = input("Enter PAYMONGO_WEBHOOK_SECRET (or press Enter to skip): ").strip()
    
    # Step 5: Summary
    print_header("Environment Variables Summary")
    
    env_vars = {
        "DJANGO_SECRET_KEY": secret_key,
        "DATABASE_URL": database_url,
        "ALLOWED_HOSTS": allowed_hosts,
        "DEBUG": "False",
        "PAYMONGO_SECRET_KEY": paymongo_secret or "sk_test_...",
        "PAYMONGO_PUBLIC_KEY": paymongo_public or "pk_test_...",
        "PAYMONGO_WEBHOOK_SECRET": paymongo_webhook or "whsk_test_..."
    }
    
    print("\nHere are your environment variables:\n")
    for key, value in env_vars.items():
        if key in ["DJANGO_SECRET_KEY", "DATABASE_URL", "PAYMONGO_SECRET_KEY", "PAYMONGO_PUBLIC_KEY", "PAYMONGO_WEBHOOK_SECRET"]:
            # Mask sensitive values
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    
    # Step 6: Instructions
    print_header("Next Steps")
    
    print("""
1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select your project: errandexpress
3. Navigate to Settings → Environment Variables
4. Add each variable from above:

   DJANGO_SECRET_KEY = [your generated key]
   DATABASE_URL = [your database URL]
   ALLOWED_HOSTS = [your allowed hosts]
   DEBUG = False
   PAYMONGO_SECRET_KEY = [your PayMongo secret key]
   PAYMONGO_PUBLIC_KEY = [your PayMongo public key]
   PAYMONGO_WEBHOOK_SECRET = [your PayMongo webhook secret]

5. Set environments to: Production, Preview, Development
6. Click "Save"
7. Redeploy your application

Alternative: Use Vercel CLI
   vercel env add DJANGO_SECRET_KEY
   vercel env add DATABASE_URL
   ... (repeat for each variable)
   vercel --prod

For more details, see: VERCEL_ENV_SETUP.md
    """)
    
    # Step 7: Save to file
    print_section("Save Configuration")
    print("Would you like to save these variables to a local .env file? (y/n)")
    print("⚠️  WARNING: Only do this for local development, NOT for production!")
    
    choice = input("Enter choice (y/n): ").strip().lower()
    if choice == 'y':
        env_file_path = Path(".env")
        with open(env_file_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print(f"\n✅ Environment variables saved to .env")
        print("⚠️  Make sure .env is in .gitignore!")
    
    print_header("Setup Complete!")
    print("""
✅ Configuration ready!

Next steps:
1. Add environment variables to Vercel Dashboard
2. Redeploy your application
3. Monitor deployment logs
4. Test your application

For support, see: VERCEL_ENV_SETUP.md
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
