# Vercel Deployment - Quick Fix

## Problem
```
Environment Variable "DJANGO_SECRET_KEY" references Secret "DJANGO_SECRET_KEY", which does not exist.
```

## Solution (5 Minutes)

### Step 1: Go to Vercel Dashboard
https://vercel.com/dashboard → Select `errandexpress` project

### Step 2: Add Environment Variables
Navigate to: **Settings** → **Environment Variables**

Add these variables:

```
DJANGO_SECRET_KEY = django-insecure-jg*nd55wqq-e!h!&@!$h4oz&)u9d^^9$xyneq#cdmug^lc+x^4
DATABASE_URL = [your PostgreSQL connection string]
ALLOWED_HOSTS = errandexpress.vercel.app,localhost,127.0.0.1
DEBUG = False
PAYMONGO_SECRET_KEY = [your PayMongo secret key]
PAYMONGO_PUBLIC_KEY = [your PayMongo public key]
PAYMONGO_WEBHOOK_SECRET = [your PayMongo webhook secret]
```

### Step 3: Set Environments
For each variable, select:
- ✅ Production
- ✅ Preview
- ✅ Development

### Step 4: Save & Redeploy
1. Click **Save**
2. Go to **Deployments**
3. Click the failed deployment
4. Click **Redeploy**

Or push to GitHub and Vercel will auto-redeploy.

## Where to Find Values

### DJANGO_SECRET_KEY
Generate new:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use existing from `.env.example`:
```
django-insecure-jg*nd55wqq-e!h!&@!$h4oz&)u9d^^9$xyneq#cdmug^lc+x^4
```

### DATABASE_URL
From your PostgreSQL provider (Supabase, Railway, etc.):
```
postgresql://username:password@host:port/database
```

### PAYMONGO Keys
From PayMongo Dashboard:
- **Secret Key**: Settings → API Keys → Secret Key
- **Public Key**: Settings → API Keys → Public Key
- **Webhook Secret**: Settings → Webhooks → Secret

## Verify Deployment

After redeploy:
1. Check deployment logs in Vercel
2. Look for: "Build completed successfully"
3. Visit your app URL
4. Test payment functionality

## Troubleshooting

| Error | Solution |
|-------|----------|
| `SECRET_KEY does not exist` | Add DJANGO_SECRET_KEY to Vercel env vars |
| `DATABASE_URL does not exist` | Add DATABASE_URL to Vercel env vars |
| `ALLOWED_HOSTS error` | Add your Vercel domain to ALLOWED_HOSTS |
| `Build fails` | Check build logs in Vercel dashboard |
| `Database connection error` | Verify DATABASE_URL is correct and accessible |

## Files Reference

- `vercel.json` - Deployment configuration
- `.env.example` - Environment variables template
- `VERCEL_ENV_SETUP.md` - Detailed setup guide
- `setup_vercel_env.py` - Interactive setup script

## Security Notes

⚠️ **NEVER commit `.env` to GitHub**
- `.env` is already in `.gitignore`
- Use Vercel secrets for sensitive data
- Rotate secrets regularly

## Next Steps

1. ✅ Add environment variables to Vercel
2. ✅ Redeploy application
3. ✅ Monitor deployment logs
4. ✅ Test payment flow
5. ✅ Monitor production logs

## Support

For detailed setup: See `VERCEL_ENV_SETUP.md`
For interactive setup: Run `python setup_vercel_env.py`
