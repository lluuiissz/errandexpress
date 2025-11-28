# PayMongo Payment Link Flow - Complete Explanation

## 🎯 Your Question Answered

**Q: Does PayMongo give us a payment link that sends back to backend that user has paid?**

**A: YES, but it works in 2 stages:**

1. **Stage 1: Payment Link** (What PayMongo gives you)
   - PayMongo creates a checkout URL: `https://paymongo.link/abc123xyz`
   - User clicks link → Pays via GCash
   - User redirected back to your app

2. **Stage 2: Webhook Confirmation** (What confirms payment)
   - PayMongo sends webhook event to your backend
   - Webhook contains payment confirmation
   - Backend updates database (marks payment as paid)
   - Chat unlocked / Task completed

---

## 🔄 Complete Payment Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    STAGE 1: PAYMENT LINK                         │
└──────────────────────────────────────────────────────────────────┘

1. User clicks "Pay ₱2"
   ↓
2. Backend creates PayMongo source
   POST /v1/sources
   {
     "type": "gcash",
     "amount": 200,
     "redirect": {
       "success": "http://127.0.0.1:8000/payment/success/",
       "failed": "http://127.0.0.1:8000/payment/failed/"
     }
   }
   ↓
3. PayMongo responds with checkout_url
   {
     "data": {
       "attributes": {
         "redirect": {
           "checkout_url": "https://paymongo.link/abc123xyz"
         }
       }
     }
   }
   ↓
4. Backend redirects user to checkout_url
   redirect("https://paymongo.link/abc123xyz")
   ↓
5. User sees PayMongo GCash payment page
   ├─ Scans QR code
   ├─ Logs into GCash
   └─ Confirms payment
   ↓
6. PayMongo processes payment
   ↓
7. User redirected back to your app
   redirect("http://127.0.0.1:8000/payment/success/?task_id=xyz")
   ↓
8. User sees success page (but payment NOT YET CONFIRMED IN DB)

┌──────────────────────────────────────────────────────────────────┐
│                  STAGE 2: WEBHOOK CONFIRMATION                   │
└──────────────────────────────────────────────────────────────────┘

9. PayMongo sends webhook to your backend
   POST /webhook/paymongo/
   {
     "data": {
       "attributes": {
         "type": "payment.paid",
         "data": {
           "attributes": {
             "amount": 200,
             "description": "ErrandExpress System Fee - Task xyz"
           }
         }
       }
     }
   }
   ↓
10. Backend webhook handler processes event
    ├─ Extracts payment amount & description
    ├─ Finds task ID from description
    ├─ Updates SystemCommission status to "paid"
    ├─ Sets task.chat_unlocked = True
    └─ Saves to database
    ↓
11. NOW the payment is confirmed in your database ✅
    ├─ Chat is unlocked
    ├─ User can message
    └─ Payment is recorded
```

---

## ⚠️ Why You Saw Only Dashboard Redirect

**The issue you experienced:**
- User paid via GCash
- Got redirected to dashboard
- But chat wasn't unlocked
- Payment wasn't recorded in database

**Root Cause:**
The webhook wasn't being received or processed correctly. Here's why:

### Problem 1: Webhook Not Exposed to PayMongo
```
Your local server: http://127.0.0.1:8000/webhook/paymongo/
PayMongo can't reach: 127.0.0.1 (localhost)

Solution: Use ngrok to expose webhook
ngrok http 8000
→ https://abc123.ngrok.io/webhook/paymongo/
```

### Problem 2: Webhook URL Not Configured
```python
# PayMongo doesn't know where to send webhook
# You need to register webhook endpoint in PayMongo dashboard
# OR create webhook programmatically

PayMongo Dashboard → Developers → Webhooks
→ Add: https://your-domain.com/webhook/paymongo/
→ Events: payment.paid, source.chargeable
```

### Problem 3: Redirect URLs Not Matching
```python
# WRONG - Using localhost
"redirect": {
    "success": "http://127.0.0.1:8000/payment/success/",
    "failed": "http://127.0.0.1:8000/payment/failed/"
}

# CORRECT - Using domain
"redirect": {
    "success": "https://your-domain.com/payment/success/",
    "failed": "https://your-domain.com/payment/failed/"
}
```

---

## 🔍 How It Should Work (Correct Flow)

### Step 1: User Initiates Payment
```python
# User clicks "Pay ₱2"
# Backend creates GCash source
result = payments.process_gcash_payment(
    amount=2.00,
    description=f"ErrandExpress System Fee - {task.id}"
)

# Returns checkout_url
return redirect(result['checkout_url'])
```

### Step 2: User Pays on PayMongo
```
User redirected to: https://paymongo.link/abc123xyz
↓
PayMongo hosted page shows GCash option
↓
User scans QR / logs into GCash
↓
Payment successful
↓
PayMongo redirects back to: /payment/success/?task_id=xyz
```

### Step 3: Webhook Confirms Payment (CRITICAL!)
```python
# PayMongo sends webhook to your backend
@csrf_exempt
def paymongo_webhook(request):
    """
    🔔 COMPREHENSIVE PAYMENT WEBHOOK HANDLER
    Handles both ₱2 system fees and main task payments
    """
    
    event = json.loads(request.body)
    event_type = event["data"]["attributes"]["type"]
    
    if event_type == "payment.paid":
        # Extract payment info
        description = event["data"]["attributes"]["data"]["attributes"]["description"]
        amount_centavos = event["data"]["attributes"]["data"]["attributes"]["amount"]
        amount_pesos = amount_centavos / 100
        
        # Check if it's ₱2 system fee
        if "System Fee" in description or amount_pesos == 2.0:
            task_id = description.split(" ")[-1]
            
            # Update database
            task = Task.objects.get(id=task_id)
            commission = SystemCommission.objects.get(task=task)
            
            # 🔔 MARK AS PAID
            commission.status = 'paid'
            commission.paid_at = timezone.now()
            commission.save()
            
            # 🔔 UNLOCK CHAT
            task.chat_unlocked = True
            task.save()
            
            # Notify user
            Notification.objects.create(
                user=task.poster,
                type='payment_confirmed',
                title='₱2 System Fee Paid! 💳',
                message=f'Chat unlocked for "{task.title}"',
                related_task=task
            )
            
            logger.info(f"✅ Payment confirmed - chat unlocked for task {task_id}")
```

### Step 4: User Sees Chat Unlocked
```
User refreshes page
↓
Backend checks: task.chat_unlocked = True
↓
Chat is now available
↓
User can message
```

---

## 📊 Payment Status Flow

```
BEFORE Payment:
├─ task.chat_unlocked = False
├─ commission.status = "pending"
└─ User cannot chat

DURING Payment:
├─ User on PayMongo checkout page
├─ Payment processing
└─ User redirected to /payment/success/

AFTER Payment (Without Webhook):
├─ task.chat_unlocked = False ❌ STILL LOCKED
├─ commission.status = "pending" ❌ STILL PENDING
└─ User cannot chat ❌ PROBLEM!

AFTER Payment (With Webhook):
├─ task.chat_unlocked = True ✅ UNLOCKED
├─ commission.status = "paid" ✅ PAID
└─ User can chat ✅ WORKS!
```

---

## 🔧 What You Need to Fix

### Issue: Webhook Not Working

**Current Code** (`core/views.py` lines 3171-3304):
```python
@csrf_exempt
def paymongo_webhook(request):
    """Webhook handler"""
    # This code EXISTS but webhook might not be reaching it
```

**Why Webhook Might Not Be Reaching**:

1. **Local Development Issue**
   ```
   Problem: PayMongo can't reach http://127.0.0.1:8000
   Solution: Use ngrok
   
   $ ngrok http 8000
   → https://abc123.ngrok.io
   
   Then tell PayMongo:
   Webhook URL: https://abc123.ngrok.io/webhook/paymongo/
   ```

2. **Production Issue**
   ```
   Problem: Webhook URL not registered in PayMongo
   Solution: Register webhook endpoint
   
   PayMongo Dashboard → Developers → Webhooks
   → Add endpoint: https://your-domain.com/webhook/paymongo/
   → Subscribe to: payment.paid, source.chargeable
   ```

3. **ALLOWED_HOSTS Issue**
   ```python
   # In settings.py
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']
   
   # Make sure your domain is included
   ```

---

## ✅ Complete Working Flow

### What PayMongo Gives You

1. **Checkout URL** (Payment Link)
   ```
   https://paymongo.link/abc123xyz
   ```
   - User clicks this link
   - Pays via GCash
   - Gets redirected back to your app

2. **Webhook Event** (Payment Confirmation)
   ```json
   {
     "data": {
       "attributes": {
         "type": "payment.paid",
         "data": {
           "attributes": {
             "amount": 200,
             "description": "ErrandExpress System Fee - task-id-xyz"
           }
         }
       }
     }
   }
   ```
   - Sent to your webhook endpoint
   - Confirms payment was successful
   - You update database

### What You Need to Do

1. **Backend**: Webhook handler exists ✅ (already implemented)
2. **PayMongo**: Register webhook endpoint ⚠️ (might be missing)
3. **Local Dev**: Use ngrok to expose webhook ⚠️ (might be missing)
4. **Settings**: Configure ALLOWED_HOSTS ⚠️ (might be incomplete)

---

## 🎯 Summary

**Q: Does PayMongo give payment link that sends confirmation to backend?**

**A: YES, in 2 parts:**

| Part | What It Is | Who Sends | What Happens |
|------|-----------|-----------|--------------|
| **Payment Link** | `https://paymongo.link/abc123xyz` | PayMongo | User pays via GCash |
| **Webhook** | POST event to `/webhook/paymongo/` | PayMongo | Backend confirms payment |

**Why You Saw Only Dashboard Redirect:**
- ✅ Payment link worked (user paid)
- ✅ Redirect worked (user came back)
- ❌ Webhook didn't work (payment not confirmed in DB)
- ❌ Chat not unlocked (because webhook didn't update DB)

**To Fix:**
1. Register webhook endpoint in PayMongo dashboard
2. Use ngrok for local development
3. Ensure webhook URL is accessible
4. Test webhook by checking logs

---

## 🔗 Related Files

- **Webhook Handler**: `core/views.py` lines 3171-3304
- **GCash Payment**: `core/paymongo.py` lines 267-295
- **System Fee View**: `core/views.py` lines 1486-1546
- **Models**: `core/models.py` (SystemCommission, Payment)

---

## 📝 Testing Webhook Locally

```bash
# 1. Start ngrok
ngrok http 8000

# 2. Copy ngrok URL (e.g., https://abc123.ngrok.io)

# 3. Register in PayMongo Dashboard
# Webhook URL: https://abc123.ngrok.io/webhook/paymongo/

# 4. Make payment test
# User pays via GCash

# 5. Check Django logs
# Should see: "✅ Payment confirmed - chat unlocked for task xyz"

# 6. Verify database
# SELECT * FROM core_systemcommission WHERE task_id='xyz'
# → status should be 'paid'
```

---

## ✨ Key Takeaway

**PayMongo gives you TWO things:**

1. **Payment Link** (checkout_url)
   - For user to pay
   - Redirects back to your app

2. **Webhook Event** (payment.paid)
   - To confirm payment in your backend
   - Updates database
   - Unlocks chat

**Both are needed for complete flow!**

If you only have the payment link but not the webhook confirmation, the payment won't be recorded in your database, and chat won't unlock.

Your system has both implemented ✅, but the webhook might not be configured correctly in PayMongo dashboard or accessible during local development.
