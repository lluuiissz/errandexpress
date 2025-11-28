# Vercel Environment Variables Setup Guide

## Problem
Vercel deployment failing with: `Environment Variable "DJANGO_SECRET_KEY" references Secret "DJANGO_SECRET_KEY", which does not exist.`

## Solution

### Step 1: Generate Required Values

#### 1. Django Secret Key
Run this command to generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Example output:
```
django-insecure-abc123xyz789...
```

#### 2. Collect Other Required Values
You'll need:
- `DATABASE_URL` - Your PostgreSQL connection string
- `PAYMONGO_SECRET_KEY` - From PayMongo dashboard
- `PAYMONGO_PUBLIC_KEY` - From PayMongo dashboard
- `PAYMONGO_WEBHOOK_SECRET` - From PayMongo dashboard (optional)

### Step 2: Add Environment Variables to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Add Environment Variables**:
   ```bash
   vercel env add DJANGO_SECRET_KEY
   vercel env add DATABASE_URL
   vercel env add ALLOWED_HOSTS
   vercel env add DEBUG
   vercel env add PAYMONGO_SECRET_KEY
   vercel env add PAYMONGO_PUBLIC_KEY
   vercel env add PAYMONGO_WEBHOOK_SECRET
   ```

   When prompted, enter the values for each variable.

4. **Pull Environment Variables Locally** (optional):
   ```bash
   vercel env pull
   ```

#### Option B: Using Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: `errandexpress`
3. Navigate to **Settings** → **Environment Variables**
4. Add each variable:

   | Variable | Value | Environments |
   |----------|-------|--------------|
   | `DJANGO_SECRET_KEY` | Your generated secret key | Production, Preview, Development |
   | `DATABASE_URL` | Your PostgreSQL connection string | Production, Preview, Development |
   | `ALLOWED_HOSTS` | `errandexpress.vercel.app,your-domain.com` | Production, Preview, Development |
   | `DEBUG` | `False` | Production |
   | `DEBUG` | `True` | Preview, Development |
   | `PAYMONGO_SECRET_KEY` | Your PayMongo secret key | Production, Preview, Development |
   | `PAYMONGO_PUBLIC_KEY` | Your PayMongo public key | Production, Preview, Development |
   | `PAYMONGO_WEBHOOK_SECRET` | Your PayMongo webhook secret | Production, Preview, Development |

### Step 3: Verify vercel.json Configuration

Your `vercel.json` should reference these variables correctly:

```json
{
  "version": 2,
  "buildCommand": "pip install -r errandexpress/requirements.txt && python errandexpress/manage.py collectstatic --noinput",
  "outputDirectory": "staticfiles",
  "env": {
    "DJANGO_SECRET_KEY": "@DJANGO_SECRET_KEY",
    "DATABASE_URL": "@DATABASE_URL",
    "DEBUG": "False",
    "ALLOWED_HOSTS": "@ALLOWED_HOSTS",
    "PAYMONGO_SECRET_KEY": "@PAYMONGO_SECRET_KEY",
    "PAYMONGO_PUBLIC_KEY": "@PAYMONGO_PUBLIC_KEY",
    "PAYMONGO_WEBHOOK_SECRET": "@PAYMONGO_WEBHOOK_SECRET"
  },
  "functions": {
    "errandexpress/wsgi.py": {
      "memory": 1024,
      "maxDuration": 30
    }
  }
}
```

### Step 4: Redeploy

After adding environment variables:

#### Option A: Using Vercel CLI
```bash
vercel --prod
```

#### Option B: Using Vercel Dashboard
1. Go to your project
2. Click **Deployments**
3. Click the three dots on the latest failed deployment
4. Select **Redeploy**

Or simply push to your GitHub repository and Vercel will automatically redeploy.

### Step 5: Verify Deployment

1. Check deployment logs in Vercel dashboard
2. Look for successful build completion
3. Visit your deployed URL to verify it's working

## Troubleshooting

### If deployment still fails:

1. **Check Environment Variables**:
   ```bash
   vercel env ls
   ```

2. **View Build Logs**:
   - Go to Vercel Dashboard → Deployments → Click on failed deployment
   - Scroll down to see detailed error messages

3. **Common Issues**:
   - **Missing DATABASE_URL**: Ensure your database is accessible from Vercel
   - **Invalid SECRET_KEY**: Make sure it's a valid Django secret key
   - **ALLOWED_HOSTS mismatch**: Add your Vercel domain to ALLOWED_HOSTS

4. **Test Locally with Production Settings**:
   ```bash
   DEBUG=False DJANGO_SECRET_KEY=your-key python manage.py runserver
   ```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for security | `django-insecure-...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `errandexpress.vercel.app,localhost` |
| `DEBUG` | Debug mode (False for production) | `False` |

### Optional Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PAYMONGO_SECRET_KEY` | PayMongo API secret key | `sk_...` |
| `PAYMONGO_PUBLIC_KEY` | PayMongo API public key | `pk_...` |
| `PAYMONGO_WEBHOOK_SECRET` | PayMongo webhook secret | `whsk_...` |

## Security Best Practices

1. **Never commit secrets** to GitHub
2. **Use Vercel secrets** for sensitive data
3. **Rotate secrets regularly** for production
4. **Use different secrets** for staging and production
5. **Enable branch protection** on main branch

## Next Steps

1. Add all environment variables to Vercel
2. Redeploy your application
3. Monitor deployment logs
4. Test payment functionality
5. Monitor production logs for errors

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify all environment variables are set
3. Ensure database is accessible
4. Check Django settings for correct variable names
