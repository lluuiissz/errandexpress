# ErrandExpress - Firebase Deployment Guide 🚀

## Overview
This guide will help you deploy ErrandExpress to Google Cloud Platform using Firebase Hosting with Cloud Run.

## Prerequisites
1. Google Cloud Platform account
2. Firebase project created
3. Firebase CLI installed: `npm install -g firebase-tools`
4. Google Cloud SDK installed
5. Docker installed (for local testing)

## Step 1: Prepare Your Environment

### 1.1 Install Required Tools
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Install Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install

# Login to Firebase
firebase login

# Login to Google Cloud
gcloud auth login
```

### 1.2 Create Firebase Project
```bash
# Initialize Firebase in your project
cd /path/to/ErrandExpressv2/errandexpress
firebase init

# Select:
# - Hosting
# - Cloud Run (if available)
```

## Step 2: Configure Environment Variables

### 2.1 Create Production Environment File
Create a `.env.production` file with your production settings:

```env
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=your-domain.web.app,your-domain.firebaseapp.com

# Database (Supabase)
DATABASE_URL=your-supabase-connection-string

# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# PayMongo
PAYMONGO_PUBLIC_KEY=your-paymongo-public-key
PAYMONGO_SECRET_KEY=your-paymongo-secret-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Step 3: Update Django Settings for Production

### 3.1 Modify settings.py
Add these production settings:

```python
# In errandexpress/settings.py

import os
from pathlib import Path

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
# Static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files (use Google Cloud Storage in production)
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = 'your-bucket-name'
```

## Step 4: Build and Deploy

### 4.1 Create requirements.txt
Ensure all dependencies are listed:

```bash
pip freeze > requirements.txt
```

### 4.2 Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 4.3 Build Docker Image
```bash
# Build the Docker image
docker build -t errandexpress .

# Test locally
docker run -p 8080:8080 --env-file .env.production errandexpress
```

### 4.4 Deploy to Google Cloud Run
```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/errandexpress

# Deploy to Cloud Run
gcloud run deploy errandexpress \
  --image gcr.io/YOUR_PROJECT_ID/errandexpress \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat .env.production | tr '\n' ',')"
```

### 4.5 Deploy Firebase Hosting
```bash
# Deploy to Firebase Hosting
firebase deploy --only hosting
```

## Step 5: Database Migration

### 5.1 Run Migrations on Cloud Run
```bash
# Connect to your Cloud Run instance
gcloud run services update errandexpress \
  --region us-central1 \
  --command="python,manage.py,migrate"
```

### 5.2 Create Superuser
```bash
# Create admin user
gcloud run services update errandexpress \
  --region us-central1 \
  --command="python,manage.py,createsuperuser"
```

## Step 6: Configure Custom Domain (Optional)

### 6.1 Add Custom Domain to Firebase
```bash
firebase hosting:channel:deploy production --expires 30d
```

### 6.2 Update DNS Settings
Add these DNS records:
- A record: Point to Firebase Hosting IP
- CNAME: Point www to your Firebase domain

## Step 7: Set Up Continuous Deployment (Optional)

### 7.1 Create GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Firebase

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
    
    - name: Build Docker image
      run: |
        docker build -t errandexpress .
    
    - name: Deploy to Cloud Run
      uses: google-github-actions/deploy-cloudrun@v0
      with:
        service: errandexpress
        image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/errandexpress
        region: us-central1
    
    - name: Deploy to Firebase Hosting
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{ secrets.GITHUB_TOKEN }}'
        firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
        channelId: live
        projectId: ${{ secrets.FIREBASE_PROJECT_ID }}
```

## Step 8: Post-Deployment Checklist

### 8.1 Verify Deployment
- [ ] Website loads correctly
- [ ] Static files are serving
- [ ] Database connections work
- [ ] User registration works
- [ ] Task creation works
- [ ] Payment system works
- [ ] Chat unlocks after payment
- [ ] Admin panel accessible
- [ ] System wallet displays correctly

### 8.2 Monitor Performance
```bash
# View logs
gcloud run services logs read errandexpress --region us-central1

# Monitor Firebase Hosting
firebase hosting:channel:list
```

### 8.3 Set Up Monitoring
- Enable Google Cloud Monitoring
- Set up error reporting
- Configure uptime checks
- Set up alerts for critical errors

## Troubleshooting

### Common Issues

#### 1. Static Files Not Loading
```bash
# Ensure STATIC_ROOT is set correctly
python manage.py collectstatic --noinput

# Check Firebase hosting configuration
cat firebase.json
```

#### 2. Database Connection Errors
- Verify DATABASE_URL is correct
- Check Supabase connection limits
- Ensure IP whitelist includes Cloud Run IPs

#### 3. Payment Webhook Not Working
- Verify PayMongo webhook URL is updated
- Check CSRF exemption for webhook endpoint
- Ensure HTTPS is enabled

#### 4. Chat Not Unlocking
- Check SystemCommission records
- Verify webhook is receiving events
- Check task.chat_unlocked field

## Security Recommendations

1. **Enable HTTPS**: Always use HTTPS in production
2. **Rotate Secrets**: Regularly rotate API keys and secrets
3. **Database Backups**: Set up automated Supabase backups
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **CORS**: Configure CORS properly for your domain
6. **Monitoring**: Set up security monitoring and alerts

## Cost Optimization

1. **Cloud Run**: Use minimum instances = 0 for cost savings
2. **Static Files**: Use Firebase Hosting CDN for static files
3. **Database**: Monitor Supabase usage and optimize queries
4. **Caching**: Implement Redis caching for frequently accessed data

## Support

For deployment issues:
1. Check Cloud Run logs: `gcloud run services logs read errandexpress`
2. Check Firebase logs: `firebase hosting:channel:list`
3. Review Django logs in Cloud Logging
4. Contact support if needed

## Additional Resources

- [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Supabase Documentation](https://supabase.com/docs)

---

**Congratulations! Your ErrandExpress platform is now deployed to Firebase! 🎉**
