# PayMongo Webhook Secret Setup

## 🔐 What Was Added

Webhook signature verification has been implemented to ensure that webhook events are **actually from PayMongo** and not from attackers.

---

## 📋 Setup Instructions

### Step 1: Add Webhook Secret to Environment

Add this to your `.env` file:

```
PAYMONGO_WEBHOOK_SECRET=whsk_XdpbpZ1w7ebWrwFEBQhNspYp
```

**Where to find it:**
- PayMongo Dashboard → Developers → Webhooks
- Click on your webhook endpoint
- Copy the "Signing Secret" value

### Step 2: Restart Django

```bash
python manage.py runserver
```

---

## 🔐 How Signature Verification Works

### What Happens

1. **PayMongo sends webhook** with signature in header:
   ```
   X-Paymongo-Signature: abc123def456...
   ```

2. **Your backend receives webhook**:
   - Extracts signature from header
   - Calculates expected signature using webhook secret
   - Compares both signatures

3. **If signatures match** ✅:
   - Webhook is legitimate
   - Payment is processed
   - Chat is unlocked

4. **If signatures don't match** ❌:
   - Webhook is rejected
   - Returns 401 Unauthorized
   - Payment is NOT processed

### Security Benefits

- ✅ Prevents fake payment notifications
- ✅ Prevents attackers from unlocking chat without payment
- ✅ Ensures only PayMongo can trigger payments
- ✅ Industry standard (HMAC-SHA256)

---

## 📝 Expected Log Output

### Successful Verification

```
✅ Webhook signature verified
🔔 PayMongo webhook received: payment.paid
💰 Payment received: ₱2.0 - Description: ErrandExpress System Fee - Task Title
✅ System fee payment CONFIRMED - chat unlocked for task [task_id]
```

### Failed Verification

```
❌ Invalid webhook signature. Expected: abc123..., Got: xyz789...
```

### Missing Secret (Development Only)

```
⚠️ PAYMONGO_WEBHOOK_SECRET not configured - skipping signature verification
```

---

## 🔧 Code Changes

### File: `errandexpress/settings.py` (Line 151)

```python
PAYMONGO_WEBHOOK_SECRET = os.getenv("PAYMONGO_WEBHOOK_SECRET")
```

### File: `core/views.py` (Lines 3202-3223)

```python
# 🔐 VERIFY WEBHOOK SIGNATURE
webhook_secret = settings.PAYMONGO_WEBHOOK_SECRET
if webhook_secret:
    # Get signature from header
    signature = request.headers.get('X-Paymongo-Signature', '')
    
    # Calculate expected signature
    body = request.body
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Verify signature
    if not hmac.compare_digest(signature, expected_signature):
        logger.error(f"❌ Invalid webhook signature...")
        return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    logger.info(f"✅ Webhook signature verified")
```

---

## ✅ Testing

### Test with Signature Verification

1. Add webhook secret to `.env`:
   ```
   PAYMONGO_WEBHOOK_SECRET=whsk_XdpbpZ1w7ebWrwFEBQhNspYp
   ```

2. Restart Django

3. Make a test payment

4. Check logs for:
   ```
   ✅ Webhook signature verified
   ```

### Test Without Signature (Development)

If you don't have the secret:
- System will skip verification
- Logs will show: `⚠️ PAYMONGO_WEBHOOK_SECRET not configured`
- Webhooks will still work (less secure)

---

## 🚀 Production Checklist

- [ ] Add `PAYMONGO_WEBHOOK_SECRET` to `.env`
- [ ] Restart Django server
- [ ] Make test payment
- [ ] Verify logs show: `✅ Webhook signature verified`
- [ ] Verify chat unlocks after payment
- [ ] Check database for payment record

---

## 🔗 Related Files

- **Settings**: `errandexpress/settings.py` line 151
- **Webhook Handler**: `core/views.py` lines 3189-3230
- **Imports**: `core/views.py` lines 38-39 (hmac, hashlib)

---

## 📞 Troubleshooting

### Issue: "Invalid webhook signature"

**Possible causes:**
1. Wrong webhook secret in `.env`
2. Webhook secret not reloaded (restart Django)
3. PayMongo sending from different endpoint

**Solution:**
1. Verify secret in PayMongo dashboard
2. Restart Django: `python manage.py runserver`
3. Check webhook endpoint URL matches

### Issue: "PAYMONGO_WEBHOOK_SECRET not configured"

**Solution:**
1. Add to `.env`: `PAYMONGO_WEBHOOK_SECRET=whsk_...`
2. Restart Django
3. Verify `.env` file is being loaded

---

## ✨ Summary

Your webhook is now **secure** with signature verification:

✅ **Only PayMongo can trigger payments**
✅ **Prevents fake payment notifications**
✅ **Industry standard HMAC-SHA256**
✅ **Detailed logging for debugging**

All payment features are now protected! 🔐
