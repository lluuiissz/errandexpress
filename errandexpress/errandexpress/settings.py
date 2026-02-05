"""
Django settings for ErrandExpress project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
# SECRET_KEY must be set in environment variables for security
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY environment variable must be set. "
        "Generate a secure key using: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# DEBUG should be False by default for security (explicitly set to True in development)
DEBUG = os.getenv("DEBUG", "False") == "True"

# ALLOWED_HOSTS configuration
ALLOWED_HOSTS_STR = os.getenv("ALLOWED_HOSTS", "")
if ALLOWED_HOSTS_STR:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(",") if host.strip()]
else:
    # Default to localhost only in DEBUG mode
    if DEBUG:
        ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
    else:
        raise ValueError(
            "ALLOWED_HOSTS environment variable must be set in production. "
            "Example: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com"
        )

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "corsheaders",  # Temporarily disabled - install with: pip install django-cors-headers
    # "rest_framework",  # Temporarily disabled - install with: pip install djangorestframework
    "core",
]

# Conditionally add storages if available (for Vercel compatibility)
try:
    import storages
    INSTALLED_APPS.append("storages")
except ImportError:
    pass  # storages not available, will use default file storage

MIDDLEWARE = [
    # "corsheaders.middleware.CorsMiddleware",  # Temporarily disabled
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add for Vercel static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "errandexpress.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.user_stats",
            ],
        },
    },
]

WSGI_APPLICATION = "errandexpress.wsgi.application"

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    # ✅ PERFORMANCE: Add connection pooling to reduce connection overhead
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Keep connections alive for 10 minutes
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,  # 10 second connection timeout
        'options': '-c statement_timeout=30000'  # 30 second query timeout
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration for Vercel
# Supabase Storage (S3 Compatible)
AWS_ACCESS_KEY_ID = "ee340b613198c6dc9fc1e22fb4247a41"
AWS_SECRET_ACCESS_KEY = "1a6c352dd6505265b342ae34c7c5a93b60e3d958129ba14e5c98ed9ae1ea7577"
AWS_STORAGE_BUCKET_NAME = "errand-uploads"
AWS_S3_ENDPOINT_URL = "https://yrkvxspmazdrfpbwerzm.storage.supabase.co/storage/v1/s3"
AWS_S3_REGION_NAME = "ap-south-1"  # Matches DB region (aws-1-ap-south-1)
AWS_DEFAULT_ACL = None  # Supabase handles permissions via Policies, not ACLs
AWS_S3_FILE_OVERWRITE = True  # Bypass HeadObject check to avoid 403 if List/Get is restricted
AWS_QUERYSTRING_AUTH = False
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_SIGNATURE_VERSION = "s3v4"

# Use Supabase Public URL for accessing files (bypasses S3 API signature checks)
# Format: https://<project_id>.supabase.co/storage/v1/object/public/<bucket_name>
SUPABASE_PROJECT_ID = "yrkvxspmazdrfpbwerzm"
AWS_S3_CUSTOM_DOMAIN = f"{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "core.User"

# Auth Redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Session settings
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 86400  # 24 hours

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:60064",  # Browser preview proxy
]

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# ✅ PERFORMANCE: Caching Configuration
# Using LocMemCache for development (no Redis required)
# For production, switch to Redis for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'errandexpress-cache',
        'TIMEOUT': 60,  # Default cache timeout: 60 seconds
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# PayMongo settings
PAYMONGO_SECRET_KEY = os.getenv("PAYMONGO_SECRET_KEY")
PAYMONGO_PUBLIC_KEY = os.getenv("PAYMONGO_PUBLIC_KEY")
PAYMONGO_WEBHOOK_SECRET = os.getenv("PAYMONGO_WEBHOOK_SECRET")

# Google Forms/Sheets settings
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
TYPING_TEST_SHEET_ID = os.getenv("TYPING_TEST_SHEET_ID")

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Logging configuration
# Vercel has a read-only filesystem, so we only use console logging in production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
