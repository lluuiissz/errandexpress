# Vercel Quick Start - 5 Minutes to Deploy

## Step 1: Prepare (2 minutes)

```bash
# Make sure all changes are committed
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

## Step 2: Create Vercel Account (1 minute)

1. Go to https://vercel.com
2. Click "Sign Up"
3. Choose "Continue with GitHub"
4. Authorize Vercel to access your GitHub account

## Step 3: Deploy (1 minute)

1. In Vercel dashboard, click "New Project"
2. Select your `errandexpress` repository
3. Click "Import"
4. Vercel will auto-detect Django project

## Step 4: Set Environment Variables (1 minute)

Before clicking "Deploy", add these variables:

```
DJANGO_SECRET_KEY = your-secret-key
DATABASE_URL = postgresql://user:pass@db.supabase.co:5432/postgres
DEBUG = False
ALLOWED_HOSTS = your-project.vercel.app
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your-supabase-key
PAYMONGO_SECRET_KEY = sk_test_xxxxx
PAYMONGO_PUBLIC_KEY = pk_test_xxxxx
PAYMONGO_WEBHOOK_SECRET = whsec_xxxxx
```

## Step 5: Deploy

1. Click "Deploy"
2. Wait 2-3 minutes for build to complete
3. Your app is live! 🎉

## Get Your Environment Variables

### DJANGO_SECRET_KEY
Generate a new one:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### DATABASE_URL
From Supabase:
1. Go to https://supabase.com
2. Select your project
3. Settings → Database → Connection string
4. Copy the PostgreSQL connection string

### SUPABASE_URL & SUPABASE_KEY
From Supabase:
1. Settings → API
2. Copy `Project URL` and `anon public` key

### PayMongo Keys
From PayMongo:
1. Go to https://dashboard.paymongo.com
2. Developers → API Keys
3. Copy Secret Key and Public Key
4. Developers → Webhooks → Copy Webhook Secret

## After Deployment

1. **Test your app:**
   - Visit `https://your-project.vercel.app`
   - Try login/signup
   - Create a task
   - Test messaging

2. **Update PayMongo webhook:**
   - Go to PayMongo dashboard
   - Developers → Webhooks
   - Update webhook URL to: `https://your-project.vercel.app/webhook/paymongo/`

3. **Set up custom domain (optional):**
   - In Vercel dashboard → Settings → Domains
   - Add your custom domain
   - Update DNS records

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check environment variables are all set |
| Static files 404 | Run `python manage.py collectstatic --noinput` locally |
| Database error | Verify DATABASE_URL format and Supabase is running |
| Webhook not working | Update webhook URL in PayMongo dashboard |

## That's It! 🚀

Your ErrandExpress app is now deployed on Vercel!

For more details, see:
- `VERCEL_DEPLOYMENT_GUIDE.md` - Comprehensive guide
- `VERCEL_SETUP_SUMMARY.md` - Detailed summary
- `README.md` - Project overview
