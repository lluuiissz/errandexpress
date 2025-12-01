# Vercel Deployment Configuration Guide

## ✅ Complete Checklist for Successful Deployment

### 1. Environment Variables (CRITICAL - Must be set in Vercel Dashboard)

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Add these variables for **Production, Preview, and Development**:

| Variable | Value | Notes |
|----------|-------|-------|
| `DJANGO_SECRET_KEY` | `(u-a=4n#($(jtcmlk*$-2235n&k-_^o1ivcz2()6yhgypx7@0s` | Generated secret key |
| `DATABASE_URL` | `sqlite:///db.sqlite3` OR your PostgreSQL URL | Use PostgreSQL for production |
| `ALLOWED_HOSTS` | `your-project.vercel.app,.vercel.app` | Replace with your actual domain |
| `DEBUG` | `False` | Must be False for production |
| `PAYMONGO_SECRET_KEY` | Your PayMongo secret key | Optional - for payments |
| `PAYMONGO_PUBLIC_KEY` | Your PayMongo public key | Optional - for payments |
| `PAYMONGO_WEBHOOK_SECRET` | Your PayMongo webhook secret | Optional - for payments |

### 2. Project Structure

```
ErrandExpressv2/
├── vercel_app.py          # Main entry point for Vercel
├── vercel.json            # Vercel configuration
├── requirements.txt       # Python dependencies (in root)
├── api/
│   └── index.py          # Alternative handler
└── errandexpress/        # Django project
    ├── manage.py
    ├── requirements.txt  # Original requirements
    ├── db.sqlite3
    ├── errandexpress/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── core/
        ├── models.py
        ├── views.py
        └── templates/
```

### 3. Key Files Explained

#### vercel_app.py
- Entry point for Vercel serverless function
- Sets up Python path to find Django
- Initializes Django with `django.setup()`
- Exports WSGI application as `app` and `handler`

#### vercel.json
- Tells Vercel to build `vercel_app.py` as a Python function
- Routes all requests to the Django app
- No static build needed (Django serves static files)

#### requirements.txt (root)
- Contains all Python dependencies
- Vercel installs these automatically
- Must be in root directory

### 4. Static Files Handling

Django's `settings.py` has:
```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # errandexpress/staticfiles/
```

**For Vercel:**
- Static files are served by Django (not ideal for production)
- For better performance, use WhiteNoise (already in requirements.txt)
- Or use Vercel's CDN by uploading to `/public/static/`

### 5. Database Configuration

**Development/Testing:**
```
DATABASE_URL=sqlite:///db.sqlite3
```

**Production (Recommended):**
```
DATABASE_URL=postgresql://user:password@host:5432/database
```

Use Supabase, Railway, or Neon for free PostgreSQL hosting.

### 6. Common Errors and Solutions

#### Error: "DJANGO_SECRET_KEY references Secret which does not exist"
**Solution:** Add environment variables in Vercel Dashboard (not in vercel.json)

#### Error: "No Output Directory named 'staticfiles' found"
**Solution:** Remove `outputDirectory` from vercel.json (Django handles static files)

#### Error: "FUNCTION_INVOCATION_FAILED"
**Solution:** Check Vercel logs for specific error. Usually missing environment variables.

#### Error: "Module not found"
**Solution:** Ensure `requirements.txt` is in root directory with all dependencies

### 7. Deployment Steps

1. **Set Environment Variables** in Vercel Dashboard
2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```
3. **Vercel Auto-Deploys** from GitHub
4. **Check Logs** in Vercel Dashboard → Deployments
5. **Test Your App** at `https://your-project.vercel.app`

### 8. Post-Deployment

#### Update PayMongo Webhook URL
```
https://your-project.vercel.app/webhook/paymongo/
```

#### Run Migrations (if using PostgreSQL)
You'll need to run migrations manually or create a management endpoint.

#### Monitor Logs
Check Vercel Dashboard → Deployments → Function Logs for errors

### 9. Performance Optimization

#### Enable WhiteNoise (already installed)
In `settings.py`, ensure:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    ...
]
```

#### Use PostgreSQL
SQLite doesn't work well with serverless (file-based)

#### Cache Static Files
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 10. Troubleshooting Checklist

- [ ] Environment variables set in Vercel Dashboard
- [ ] `ALLOWED_HOSTS` includes your Vercel domain
- [ ] `DEBUG=False` in production
- [ ] `requirements.txt` in root directory
- [ ] Database accessible from Vercel
- [ ] No hardcoded secrets in code
- [ ] Static files collected (if using WhiteNoise)

### 11. Vercel Limits (Free Tier)

- ✅ 100 GB bandwidth/month
- ✅ 100 deployments/day
- ⚠️ 10-second function timeout
- ⚠️ 50 MB function size limit

### 12. Alternative: Use Vercel Postgres

Vercel offers PostgreSQL database:
```bash
vercel postgres create
```

Then use the connection string in `DATABASE_URL`.

---

## Quick Deploy Command

```bash
# 1. Ensure environment variables are set in Vercel Dashboard
# 2. Push to GitHub
git add .
git commit -m "Ready for Vercel deployment"
git push origin main

# 3. Vercel auto-deploys
# 4. Check https://your-project.vercel.app
```

---

## Support Resources

- **Vercel Docs:** https://vercel.com/docs
- **Django on Vercel:** https://vercel.com/guides/deploying-django-with-vercel
- **Troubleshooting:** Check Vercel Dashboard → Deployments → Logs

---

**Status:** ✅ Configuration optimized for Vercel deployment
**Last Updated:** 2025-12-01
