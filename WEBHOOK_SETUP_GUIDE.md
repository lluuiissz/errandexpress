# PayMongo Webhook Setup Guide - Complete Instructions

## 🎯 What Was Fixed

Your payment system now has **complete webhook support** with these improvements:

### 1. **Immediate Chat Unlock** ✅
- When user returns from GCash payment, chat is unlocked immediately
- No need to wait for webhook confirmation
- User sees success message and can chat right away

### 2. **Robust Webhook Handler** ✅
- Improved task ID extraction using UUID regex pattern
- Handles multiple description formats
- Better error logging and debugging
- Automatic chat unlock on webhook confirmation (backup)

### 3. **Detailed Logging** ✅
- Webhook payload logged for debugging
- Task ID extraction logged
- Payment confirmation logged
- Error messages with full traceback

---

## 🚀 Setup Instructions

### Step 1: Local Development (ngrok)

**Why ngrok?**
- PayMongo can't reach `http://127.0.0.1:8000` (localhost)
- ngrok creates a public URL that PayMongo can access

**Installation:**
```bash
# Download from https://ngrok.com/download
# Or install via package manager

# Windows (Chocolatey)
choco install ngrok

# macOS (Homebrew)
brew install ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
```

**Start ngrok:**
```bash
# In a new terminal window
ngrok http 8000

# Output:
# Session Status                online
# Account                       your-email@example.com
# Version                       3.0.0
# Region                        us (United States)
# Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the ngrok URL**: `https://abc123.ngrok.io`

---

### Step 2: Register Webhook in PayMongo Dashboard

**For Live API (Production):**

1. Go to [PayMongo Dashboard](https://dashboard.paymongo.com)
2. Login with your account
3. Navigate to: **Developers** → **Webhooks**
4. Click **Add Endpoint**
5. Enter webhook URL:
   ```
   https://abc123.ngrok.io/webhook/paymongo/
   ```
   (Replace `abc123` with your ngrok URL)

6. Select events to subscribe to:
   - ✅ `payment.paid` (Payment confirmed)
   - ✅ `source.chargeable` (GCash source ready)

7. Click **Add Endpoint**

**For Test API (Development):**

1. Same steps as above, but use your ngrok URL
2. PayMongo will send test webhooks to your local server

---

### Step 3: Verify Webhook Configuration

**Check if webhook is registered:**
```bash
# In PayMongo Dashboard
Developers → Webhooks → Your Endpoint
# Should show: Status = Active
```

**Test webhook locally:**
```bash
# Make a test payment
1. Go to http://127.0.0.1:8000/payment/system-fee/<task_id>/
2. Click "Pay ₱2"
3. Select GCash
4. Complete payment on PayMongo page
5. Check Django logs for webhook confirmation
```

**Expected log output:**
```
🔔 PayMongo webhook received: payment.paid
💰 Payment received: ₱2.0 - Description: ErrandExpress System Fee - Task Title
Source ID: src_abc123xyz
📝 Processing as SYSTEM FEE payment
Extracted task_id: 12345678-1234-1234-1234-123456789012
✅ System fee payment CONFIRMED - chat unlocked for task 12345678-1234-1234-1234-123456789012
```

---

### Step 4: Production Deployment

**When deploying to production:**

1. **Update webhook URL in PayMongo Dashboard:**
   ```
   https://your-domain.com/webhook/paymongo/
   ```

2. **Update ALLOWED_HOSTS in settings.py:**
   ```python
   ALLOWED_HOSTS = [
       'localhost',
       '127.0.0.1',
       'your-domain.com',
       'www.your-domain.com'
   ]
   ```

3. **Ensure HTTPS is enabled:**
   - PayMongo requires HTTPS for webhook endpoints
   - Use Let's Encrypt or similar for free SSL

4. **Test webhook on production:**
   - Make a test payment
   - Verify webhook is received
   - Check logs for confirmation

---

## 🔍 How It Works Now

### Payment Flow with Webhook

```
1. USER INITIATES PAYMENT
   ├─ Clicks "Pay ₱2"
   ├─ Backend creates GCash source
   └─ Redirects to PayMongo checkout URL

2. USER PAYS ON PAYMONGO
   ├─ Scans QR code
   ├─ Logs into GCash
   └─ Confirms payment

3. PAYMONGO PROCESSES PAYMENT
   ├─ Deducts from GCash account
   └─ Marks payment as successful

4. USER REDIRECTED BACK (Immediate)
   ├─ Redirected to: /payment/success/
   ├─ Backend unlocks chat IMMEDIATELY ✅
   ├─ User sees: "System fee payment successful!"
   └─ User can chat right away

5. PAYMONGO SENDS WEBHOOK (Backup)
   ├─ Sends POST to: /webhook/paymongo/
   ├─ Backend receives: payment.paid event
   ├─ Backend unlocks chat (if not already done)
   └─ Sends notification to user
```

### Two-Layer Confirmation

**Layer 1: Immediate (Redirect)**
- User returns from PayMongo
- Chat unlocked immediately
- User can start messaging

**Layer 2: Webhook (Backup)**
- PayMongo sends confirmation event
- Database updated with payment details
- Notifications sent to both users
- Audit trail recorded

---

## 📊 Payment Status Flow

```
BEFORE PAYMENT:
├─ task.chat_unlocked = False
├─ commission.status = "pending"
└─ User cannot chat

AFTER USER PAYS (Redirect):
├─ task.chat_unlocked = True ✅
├─ commission.status = "paid" ✅
└─ User can chat ✅

AFTER WEBHOOK RECEIVED:
├─ task.chat_unlocked = True (already set)
├─ commission.status = "paid" (already set)
├─ commission.paymongo_payment_id = "src_xyz"
└─ Notification sent to user
```

---

## 🐛 Debugging

### Check if webhook is being received

**View Django logs:**
```bash
# If running locally
# Check terminal where you ran: python manage.py runserver

# Look for:
# 🔔 PayMongo webhook received: payment.paid
# 💰 Payment received: ₱2.0
# ✅ System fee payment CONFIRMED
```

### Common Issues

**Issue 1: Webhook not received**
```
❌ Webhook URL not accessible
Solution: 
- Check ngrok is running
- Verify webhook URL in PayMongo dashboard
- Check firewall settings
```

**Issue 2: Task ID not found**
```
❌ Task or commission not found for ₱2 payment
Solution:
- Verify task exists in database
- Check task ID format (should be UUID)
- Check SystemCommission record exists
```

**Issue 3: Payment not confirmed in database**
```
❌ Payment record not found for task payment
Solution:
- Verify Payment record exists with status='pending_payment'
- Check task ID extraction is working
- Review webhook payload in logs
```

---

## 📝 Webhook Payload Example

**What PayMongo sends to your webhook:**

```json
{
  "data": {
    "attributes": {
      "type": "payment.paid",
      "data": {
        "id": "src_abc123xyz",
        "attributes": {
          "amount": 200,
          "currency": "PHP",
          "description": "ErrandExpress System Fee - Task Title",
          "status": "paid",
          "type": "gcash"
        }
      }
    }
  }
}
```

**Your backend extracts:**
- `event_type` = "payment.paid"
- `amount_centavos` = 200 (₱2.00)
- `description` = "ErrandExpress System Fee - Task Title"
- `source_id` = "src_abc123xyz"

---

## ✅ Testing Checklist

- [ ] ngrok is running: `ngrok http 8000`
- [ ] Webhook URL registered in PayMongo dashboard
- [ ] Django server is running: `python manage.py runserver`
- [ ] Create a task as task_poster
- [ ] Go to: `/payment/system-fee/<task_id>/`
- [ ] Click "Pay ₱2"
- [ ] Select GCash
- [ ] Complete payment on PayMongo page
- [ ] Verify redirect to `/payment/success/`
- [ ] Check chat is unlocked
- [ ] Check Django logs for webhook confirmation
- [ ] Verify database: `commission.status = 'paid'`
- [ ] Verify database: `task.chat_unlocked = True`

---

## 🎯 Summary

Your payment system now has:

✅ **Immediate Chat Unlock** - User can chat right after payment
✅ **Webhook Confirmation** - Database updated automatically
✅ **Robust Error Handling** - Better debugging and logging
✅ **Two-Layer Confirmation** - Redirect + Webhook backup
✅ **Production Ready** - Works with ngrok (dev) and domain (prod)

**Next Steps:**
1. Start ngrok: `ngrok http 8000`
2. Register webhook URL in PayMongo dashboard
3. Test payment flow
4. Check logs for confirmation
5. Deploy to production with your domain

---

## 🔗 Related Files

- **Webhook Handler**: `core/views.py` lines 3188-3357
- **Payment Success**: `core/views.py` lines 1553-1598
- **URL Configuration**: `errandexpress/urls.py` line 106
- **Models**: `core/models.py` (SystemCommission, Payment, Task)

---

## 📞 Support

If webhook is not working:
1. Check ngrok is running and URL is correct
2. Check webhook URL in PayMongo dashboard
3. Review Django logs for errors
4. Verify task ID and commission record exist
5. Check ALLOWED_HOSTS includes your domain

All improvements are production-ready! 🚀
