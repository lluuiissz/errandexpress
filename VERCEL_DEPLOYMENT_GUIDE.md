# Vercel Deployment Guide for ErrandExpress

## Overview

Vercel is a serverless platform that allows you to deploy your Django application without managing servers. Unlike Firebase + Cloud Run, Vercel handles everything in one place with automatic scaling and zero-downtime deployments.

## Architecture: Vercel vs Firebase + Cloud Run

### Vercel (Recommended for ErrandExpress)
```
Your Django App
    ↓
Vercel Serverless Functions (Python)
    ↓
Supabase PostgreSQL (Database)
    ↓
PayMongo (Payments)
```

**Advantages:**
- ✅ Single platform (no Firebase needed)
- ✅ Automatic static file serving
- ✅ Built-in CI/CD with GitHub integration
- ✅ Free tier available (up to 100 serverless function invocations/day)
- ✅ Easy environment variable management
- ✅ Automatic HTTPS and custom domains
- ✅ No Docker needed
- ✅ Instant deployments

### Firebase + Cloud Run (Legacy - Not Recommended)
```
Your Django App
    ↓
Docker Container
    ↓
Google Cloud Run (Backend)
    ↓
Firebase Hosting (Static Files)
    ↓
Cloud SQL (Database)
```

**Disadvantages:**
- ❌ Multiple services to manage
- ❌ More complex setup
- ❌ Higher costs
- ❌ Requires Docker knowledge
- ❌ Separate static file hosting

## Step 1: Prepare Your Project

### 1.1 Update Django Settings for Vercel

Your `settings.py` is already configured! It uses:
- Environment variables for all secrets
- `dj_database_url` for PostgreSQL connection
- WhiteNoise for static files (optional but recommended)

### 1.2 Update `.env` File

Create a `.env` file in the root directory:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.vercel.app,yourdomain.com

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# PayMongo
PAYMONGO_SECRET_KEY=sk_test_xxxxx
PAYMONGO_PUBLIC_KEY=pk_test_xxxxx
PAYMONGO_WEBHOOK_SECRET=whsec_xxxxx
```

### 1.3 Update `.gitignore`

Ensure `.env` is in `.gitignore` (already done):

```
.env
.env.local
.env.*.local
```

## Step 2: Install Vercel CLI

```bash
npm install -g vercel
```

Or if you don't have Node.js, you can deploy directly from GitHub.

## Step 3: Deploy to Vercel

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to https://vercel.com
   - Sign up or log in
   - Click "New Project"
   - Select your GitHub repository
   - Click "Import"

3. **Configure Environment Variables:**
   - In Vercel dashboard, go to Settings → Environment Variables
   - Add all variables from your `.env` file:
     - `DJANGO_SECRET_KEY`
     - `DATABASE_URL`
     - `DEBUG=False`
     - `ALLOWED_HOSTS`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `PAYMONGO_SECRET_KEY`
     - `PAYMONGO_PUBLIC_KEY`
     - `PAYMONGO_WEBHOOK_SECRET`

4. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy your app
   - Your app will be available at `https://your-project.vercel.app`

### Option B: Deploy via Vercel CLI

```bash
# Login to Vercel
vercel login

# Deploy
vercel --prod

# Follow the prompts to set environment variables
```

## Step 4: Configure Custom Domain (Optional)

1. In Vercel dashboard, go to Settings → Domains
2. Add your custom domain (e.g., `errandexpress.com`)
3. Update DNS records at your domain provider
4. Vercel will automatically provision SSL certificate

## Step 5: Set Up Database Migrations

After first deployment, run migrations:

```bash
# Via Vercel CLI
vercel env pull

# Run migrations locally (connected to production database)
python manage.py migrate --database=production
```

Or set up a migration endpoint in your Django app:

```python
# In urls.py
from django.core.management import call_command

def run_migrations(request):
    if request.user.is_staff and request.method == 'POST':
        call_command('migrate')
        return JsonResponse({'status': 'Migrations completed'})
    return JsonResponse({'error': 'Unauthorized'}, status=403)
```

## Step 6: Verify Deployment

1. **Check your app:**
   - Visit `https://your-project.vercel.app`
   - Test login, task creation, messaging, payments

2. **Check logs:**
   - In Vercel dashboard, go to Deployments → Logs
   - Look for any errors

3. **Test PayMongo webhook:**
   - Update webhook URL in PayMongo dashboard to:
     ```
     https://your-project.vercel.app/webhook/paymongo/
     ```

## Environment Variables Reference

| Variable | Value | Example |
|----------|-------|---------|
| `DJANGO_SECRET_KEY` | Your Django secret key | `django-insecure-...` |
| `DATABASE_URL` | Supabase PostgreSQL connection | `postgresql://user:pass@db.supabase.co:5432/postgres` |
| `DEBUG` | Set to `False` for production | `False` |
| `ALLOWED_HOSTS` | Your domain(s) | `yourdomain.vercel.app,yourdomain.com` |
| `SUPABASE_URL` | Your Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Your Supabase API key | `eyJhbGc...` |
| `PAYMONGO_SECRET_KEY` | PayMongo secret key | `sk_test_...` |
| `PAYMONGO_PUBLIC_KEY` | PayMongo public key | `pk_test_...` |
| `PAYMONGO_WEBHOOK_SECRET` | PayMongo webhook secret | `whsec_...` |

## Troubleshooting

### Issue: Build fails with "Python version not found"

**Solution:** Specify Python version in `vercel.json`:
```json
{
  "buildCommand": "pip install -r errandexpress/requirements.txt && python errandexpress/manage.py collectstatic --noinput",
  "functions": {
    "errandexpress/wsgi.py": {
      "runtime": "python3.9"
    }
  }
}
```

### Issue: Static files not loading

**Solution:** Ensure `STATIC_ROOT` is set in settings.py:
```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

And run:
```bash
python manage.py collectstatic --noinput
```

### Issue: Database connection fails

**Solution:** Verify `DATABASE_URL` format:
```
postgresql://username:password@host:5432/database
```

Test connection locally:
```bash
python manage.py dbshell
```

### Issue: PayMongo webhook not working

**Solution:** 
1. Update webhook URL in PayMongo dashboard
2. Verify `PAYMONGO_WEBHOOK_SECRET` is set
3. Check Vercel logs for webhook errors

### Issue: Static files return 404

**Solution:** 
1. Ensure `STATIC_URL = "/static/"` in settings.py
2. Run `collectstatic` during build
3. Check that static files are in `core/static/`

## Performance Tips

1. **Enable caching:**
   ```python
   # In settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
       }
   }
   ```

2. **Optimize database queries:**
   - Use `select_related()` and `prefetch_related()`
   - Add database indexes on frequently queried fields

3. **Compress static files:**
   - Use WhiteNoise for automatic compression
   - Minify CSS and JavaScript

4. **Monitor function duration:**
   - Keep functions under 30 seconds
   - Use background tasks for long operations

## Costs

**Vercel Free Tier:**
- ✅ 100 serverless function invocations/day
- ✅ Unlimited bandwidth
- ✅ Unlimited deployments
- ✅ Free SSL certificate
- ✅ Free custom domains

**Vercel Pro ($20/month):**
- ✅ Unlimited serverless function invocations
- ✅ Priority support
- ✅ Advanced analytics

**Supabase (Database):**
- ✅ Free tier: 500MB storage, 2GB bandwidth
- ✅ Pro tier: $25/month for more storage

**PayMongo (Payments):**
- ✅ 2.2% + ₱2.50 per transaction (GCash)
- ✅ 2.2% + ₱2.50 per transaction (Card)

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Connect GitHub to Vercel
3. ✅ Set environment variables
4. ✅ Deploy
5. ✅ Test all features
6. ✅ Set up custom domain
7. ✅ Monitor logs and performance

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Django Docs:** https://docs.djangoproject.com
- **Supabase Docs:** https://supabase.com/docs
- **PayMongo Docs:** https://developers.paymongo.com

---

**Status:** ✅ Ready for Vercel deployment
