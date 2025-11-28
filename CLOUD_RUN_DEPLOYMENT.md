# Google Cloud Run Deployment Guide

Deploy ErrandExpress Django backend to Google Cloud Run with Firebase Hosting for static files.

## 🏗️ Architecture

```
User Browser
    ↓
Firebase Hosting (Static Files)
    ↓
Cloud Run (Django Backend)
    ↓
Cloud SQL (PostgreSQL Database)
```

## 📋 Prerequisites

1. **Google Cloud Account** - https://console.cloud.google.com/
2. **Google Cloud SDK** - https://cloud.google.com/sdk/docs/install
3. **Docker** - https://www.docker.com/products/docker-desktop
4. **Firebase CLI** - `npm install -g firebase-tools`

## 🚀 Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a Project" → "New Project"
3. Name: `ErrandExpress`
4. Click "Create"
5. Wait for project to be created
6. Select the project

## 🐳 Step 2: Set Up Docker

The Dockerfile is already in your project. Verify it exists:

```bash
cat errandexpress/Dockerfile
```

If it doesn't exist, create it:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY errandexpress/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY errandexpress/ .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "errandexpress.wsgi:application"]
```

## 🔑 Step 3: Set Up Cloud SQL (PostgreSQL)

### Create PostgreSQL Instance

```bash
gcloud sql instances create errandexpress-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --availability-type=REGIONAL
```

### Create Database

```bash
gcloud sql databases create errandexpress \
  --instance=errandexpress-db
```

### Create Database User

```bash
gcloud sql users create django \
  --instance=errandexpress-db \
  --password=YOUR_SECURE_PASSWORD
```

### Get Connection String

```bash
gcloud sql instances describe errandexpress-db --format='value(connectionName)'
```

Output format: `project-id:region:instance-name`

## 🔐 Step 4: Set Up Environment Variables

Create `.env.production` in project root:

```bash
# Django
DEBUG=False
SECRET_KEY=your-very-secure-random-key-here
ALLOWED_HOSTS=your-cloud-run-url.run.app,your-domain.com

# Database (Cloud SQL)
DATABASE_URL=postgresql://django:YOUR_PASSWORD@/errandexpress?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME

# PayMongo
PAYMONGO_PUBLIC_KEY=pk_live_your_live_key
PAYMONGO_SECRET_KEY=sk_live_your_live_key

# Other settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🏗️ Step 5: Create Cloud Run Service

### Build and Push Docker Image

```bash
# Set project ID
gcloud config set project YOUR_PROJECT_ID

# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/errandexpress

# Wait for build to complete (5-10 minutes)
```

### Deploy to Cloud Run

```bash
gcloud run deploy errandexpress \
  --image gcr.io/YOUR_PROJECT_ID/errandexpress \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=False,SECRET_KEY=your-key \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --service-account=cloud-run-service@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 📊 Step 6: Run Migrations

### Get Cloud Run Service URL

```bash
gcloud run services describe errandexpress --region us-central1 --format='value(status.url)'
```

### Connect to Cloud SQL and Run Migrations

```bash
# Create Cloud SQL Proxy
cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432

# In another terminal
export DATABASE_URL="postgresql://django:PASSWORD@localhost/errandexpress"
python manage.py migrate
python manage.py createsuperuser
```

## 🔗 Step 7: Connect Firebase Hosting

### Update Firebase Configuration

Edit `errandexpress/firebase.json`:

```json
{
  "hosting": {
    "public": "staticfiles",
    "rewrites": [
      {
        "source": "**",
        "destination": "https://YOUR_CLOUD_RUN_URL"
      }
    ]
  }
}
```

### Deploy Static Files

```bash
firebase deploy --only hosting
```

## 🌐 Step 8: Configure Custom Domain

### Add Domain to Cloud Run

```bash
gcloud run domain-mappings create \
  --service=errandexpress \
  --domain=your-domain.com \
  --region=us-central1
```

### Update DNS Records

Add these DNS records at your domain registrar:

```
Type: CNAME
Name: your-domain.com
Value: ghs.googlehosted.com
```

## ✅ Verification Checklist

- [ ] Cloud SQL instance created
- [ ] Database and user created
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Migrations run successfully
- [ ] Admin user created
- [ ] Static files collected
- [ ] Firebase Hosting connected
- [ ] Custom domain configured
- [ ] SSL certificate issued

## 🧪 Testing

### Test Cloud Run Service

```bash
curl https://YOUR_CLOUD_RUN_URL/
```

Should return HTML (not error)

### Test Admin Panel

```
https://YOUR_CLOUD_RUN_URL/admin/
```

Login with superuser credentials

### Test API

```bash
curl https://YOUR_CLOUD_RUN_URL/api/tasks/
```

Should return JSON

## 🔍 Monitoring

### View Logs

```bash
gcloud run logs read errandexpress --region us-central1 --limit 50
```

### View Metrics

- Go to Cloud Run console
- Select `errandexpress` service
- Click "Metrics" tab

### Set Up Alerts

1. Go to Cloud Monitoring
2. Create alert policy
3. Set conditions (CPU, memory, error rate)
4. Add notification channels

## 💰 Cost Optimization

### Reduce Costs

1. **Use smaller instance**
   - Change `--tier=db-f1-micro` to `--tier=db-g1-small`

2. **Set auto-scaling limits**
   ```bash
   gcloud run services update errandexpress \
     --max-instances=10 \
     --min-instances=1
   ```

3. **Use Cloud CDN**
   - Cache static files
   - Reduce origin requests

4. **Schedule downtime**
   - Stop Cloud SQL during off-hours
   - Use Cloud Scheduler

### Estimated Monthly Cost

- Cloud Run: $0.40/million requests (~$10-20/month for 50k requests)
- Cloud SQL: $15-30/month (db-f1-micro)
- Cloud Storage: $0.02/GB (~$1-5/month)
- **Total: ~$30-50/month**

## 🚨 Troubleshooting

### Cloud Run Service Won't Start

```bash
# Check logs
gcloud run logs read errandexpress --limit 100

# Common issues:
# 1. Missing environment variables
# 2. Database connection failed
# 3. Port not 8080
# 4. Migrations not run
```

### Database Connection Failed

```bash
# Verify Cloud SQL instance
gcloud sql instances describe errandexpress-db

# Check firewall rules
gcloud sql instances patch errandexpress-db \
  --require-ssl=false
```

### Static Files Not Loading

```bash
# Verify Firebase config
firebase hosting:channel:list

# Redeploy
firebase deploy --only hosting
```

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)
- [Django Deployment Guide](https://docs.djangoproject.com/en/4.2/howto/deployment/)

## 🔒 Security Best Practices

1. **Use Secret Manager**
   ```bash
   gcloud secrets create django-secret-key --data-file=-
   ```

2. **Enable VPC Connector**
   - Isolate Cloud Run from public internet
   - Connect only to Cloud SQL

3. **Set Up IAM Roles**
   - Principle of least privilege
   - Only grant necessary permissions

4. **Enable Cloud Audit Logs**
   - Track all API calls
   - Monitor security events

5. **Use HTTPS Only**
   - Enforce SSL/TLS
   - Set `SECURE_SSL_REDIRECT=True`

## 📞 Support

For issues:
1. Check Cloud Run logs: `gcloud run logs read errandexpress`
2. Check Cloud SQL logs: `gcloud sql operations list`
3. Review error messages carefully
4. Check Django debug page (if DEBUG=True temporarily)

---

**Your ErrandExpress app is now live on Google Cloud! 🎉**
