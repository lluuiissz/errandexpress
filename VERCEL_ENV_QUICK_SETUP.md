# Quick Environment Variable Setup Guide for Vercel

## 🚨 CRITICAL: Add These Environment Variables NOW

Go to: **https://vercel.com/dashboard** → **Your Project** → **Settings** → **Environment Variables**

### Required Variables (Add ALL of these):

```
DJANGO_SECRET_KEY
Value: (u-a=4n#($(jtcmlk*$-2235n&k-_^o1ivcz2()6yhgypx7@0s
Environments: ✅ Production ✅ Preview ✅ Development
```

```
ALLOWED_HOSTS
Value: .vercel.app
Environments: ✅ Production ✅ Preview ✅ Development
```

```
DEBUG
Value: False
Environments: ✅ Production ✅ Preview ✅ Development
```

```
DATABASE_URL
Value: sqlite:///db.sqlite3
Environments: ✅ Production ✅ Preview ✅ Development
```

### Optional (for PayMongo payments):

```
PAYMONGO_SECRET_KEY
Value: sk_test_your_key_here
Environments: ✅ Production ✅ Preview ✅ Development
```

```
PAYMONGO_PUBLIC_KEY
Value: pk_test_your_key_here
Environments: ✅ Production ✅ Preview ✅ Development
```

---

## 📝 How to Add Variables in Vercel Dashboard

1. Click **"Add New"** button
2. Enter **Key** (e.g., `DJANGO_SECRET_KEY`)
3. Enter **Value** (copy from above)
4. Check **ALL THREE** environment boxes:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Click **"Save"**
6. Repeat for each variable

---

## 🔄 After Adding Variables

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click **"Redeploy"** button
4. Wait for deployment to complete
5. Visit your app URL

---

## ⚠️ Common Mistakes

❌ **Don't** add quotes around values  
❌ **Don't** forget to check all three environment boxes  
❌ **Don't** skip any required variables  
✅ **Do** copy values exactly as shown  
✅ **Do** redeploy after adding variables  

---

## 🆘 Still Not Working?

If you still see errors after adding variables:

1. Check Vercel Dashboard → Deployments → Function Logs
2. Look for specific error messages
3. The new `vercel_app.py` will show detailed errors
4. Share the error message for help

---

**Status:** Waiting for environment variables to be set in Vercel Dashboard
