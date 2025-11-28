# Cloud Run Quick Start (5 Minutes)

Fast-track deployment to Google Cloud Run.

## ⚡ Quick Setup

### 1. Install Google Cloud SDK

**Windows:**
```bash
# Download and run installer
# https://cloud.google.com/sdk/docs/install-sdk#windows

# Or use Chocolatey
choco install google-cloud-sdk
```

**Verify installation:**
```bash
gcloud --version
```

### 2. Authenticate

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Create Cloud SQL Database

```bash
# Create PostgreSQL instance (takes 5-10 minutes)
gcloud sql instances create errandexpress-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create errandexpress \
  --instance=errandexpress-db

# Create user
gcloud sql users create django \
  --instance=errandexpress-db \
  --password=SecurePassword123!
```

### 4. Deploy to Cloud Run

```bash
# From project root
cd ErrandExpressv2

# Build and deploy
gcloud run deploy errandexpress \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=False \
  --add-cloudsql-instances PROJECT_ID:us-central1:errandexpress-db
```

### 5. Get Your URL

```bash
gcloud run services describe errandexpress \
  --region us-central1 \
  --format='value(status.url)'
```

Output: `https://errandexpress-xxxxx.run.app`

### 6. Run Migrations

```bash
# Option A: Use Cloud SQL Proxy
cloud_sql_proxy -instances=PROJECT_ID:us-central1:errandexpress-db=tcp:5432

# In another terminal
export DATABASE_URL="postgresql://django:SecurePassword123!@localhost/errandexpress"
cd errandexpress
python manage.py migrate
python manage.py createsuperuser
```

### 7. Test Your App

```bash
# Test homepage
curl https://errandexpress-xxxxx.run.app/

# Test admin
https://errandexpress-xxxxx.run.app/admin/
```

## 🔧 Environment Variables

Update in Cloud Run console:

```
DEBUG=False
SECRET_KEY=your-very-secure-key-here
ALLOWED_HOSTS=errandexpress-xxxxx.run.app,your-domain.com
DATABASE_URL=postgresql://django:PASSWORD@/errandexpress?host=/cloudsql/PROJECT_ID:us-central1:errandexpress-db
PAYMONGO_PUBLIC_KEY=pk_live_your_key
PAYMONGO_SECRET_KEY=sk_live_your_key
```

## 📊 Monitoring

```bash
# View logs
gcloud run logs read errandexpress --limit 50

# View metrics
gcloud run services describe errandexpress --region us-central1
```

## 🚀 Auto-Deploy from GitHub

1. Go to Cloud Run console
2. Click "Create Service"
3. Select "Continuously deploy from a Git repository"
4. Connect GitHub account
5. Select `lluuiissz/errandexpress`
6. Choose branch: `main`
7. Set build settings
8. Deploy

Now every push to `main` auto-deploys!

## 💾 Backup Database

```bash
# Export database
gcloud sql export sql errandexpress-db \
  gs://YOUR_BUCKET/backup-$(date +%Y%m%d).sql \
  --database=errandexpress
```

## 🗑️ Cleanup (Delete Everything)

```bash
# Delete Cloud Run service
gcloud run services delete errandexpress --region us-central1

# Delete Cloud SQL instance
gcloud sql instances delete errandexpress-db

# Delete Cloud Storage bucket
gsutil -m rm -r gs://YOUR_BUCKET
```

## 📞 Troubleshooting

### Service won't start
```bash
gcloud run logs read errandexpress --limit 100
```

### Database connection failed
```bash
# Check Cloud SQL instance
gcloud sql instances describe errandexpress-db

# Verify firewall
gcloud sql instances patch errandexpress-db --require-ssl=false
```

### Static files not loading
```bash
# Rebuild and redeploy
gcloud run deploy errandexpress \
  --source . \
  --region us-central1
```

## 📈 Estimated Costs

- **Cloud Run**: $0.40 per 1M requests (~$10/month for typical usage)
- **Cloud SQL**: $15-30/month (db-f1-micro)
- **Storage**: ~$1-5/month
- **Total**: ~$30-50/month

## ✅ Checklist

- [ ] Google Cloud SDK installed
- [ ] Authenticated with gcloud
- [ ] Cloud SQL instance created
- [ ] Cloud Run service deployed
- [ ] Migrations run
- [ ] Admin user created
- [ ] App accessible at URL
- [ ] Environment variables set
- [ ] GitHub auto-deploy configured (optional)

---

**Your app is now live! 🎉**

Visit: `https://errandexpress-xxxxx.run.app`
