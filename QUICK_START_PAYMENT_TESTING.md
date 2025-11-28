# Quick Start - Payment Testing Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start ngrok (Terminal 1)
```bash
ngrok http 8000
# Copy the URL: https://abc123.ngrok.io
```

### Step 2: Register Webhook (PayMongo Dashboard)
1. Go to: https://dashboard.paymongo.com
2. Navigate to: **Developers** → **Webhooks**
3. Click **Add Endpoint**
4. Enter: `https://abc123.ngrok.io/webhook/paymongo/`
5. Select events: ✅ `payment.paid` ✅ `source.chargeable`
6. Click **Add Endpoint**

### Step 3: Start Django (Terminal 2)
```bash
python manage.py runserver
```

### Step 4: Test Payment Flow
1. Go to: http://127.0.0.1:8000/signup/
2. Create account as **task_poster**
3. Go to: http://127.0.0.1:8000/tasks/create/
4. Create a task (any category)
5. Go to: http://127.0.0.1:8000/payment/system-fee/<task_id>/
6. Click "Pay ₱2"
7. Select **GCash**
8. Complete payment on PayMongo page
9. ✅ Chat should be unlocked immediately!

---

## 📊 What Happens

```
You Click "Pay ₱2"
    ↓
Backend creates GCash source
    ↓
You redirected to: https://paymongo.link/abc123xyz
    ↓
You pay via GCash (test mode)
    ↓
You redirected back to: /payment/success/
    ↓
✅ Chat is UNLOCKED immediately
✅ You can message
✅ Notification sent
    ↓
(Background) PayMongo sends webhook confirmation
    ↓
Database updated with payment details
```

---

## ✅ Verification

### Check Chat is Unlocked
1. Go to task detail page
2. Look for **Chat** section
3. Should show message input box (not locked)

### Check Database
```bash
# In Django shell
python manage.py shell

from core.models import Task, SystemCommission
task = Task.objects.first()
print(f"Chat unlocked: {task.chat_unlocked}")  # Should be True
print(f"Commission status: {task.commission.status}")  # Should be 'paid'
```

### Check Logs
```bash
# In Terminal 2 (Django server)
# Look for:
🔔 PayMongo webhook received: payment.paid
✅ System fee payment CONFIRMED - chat unlocked for task [task_id]
```

---

## 🐛 Troubleshooting

### Issue: Chat not unlocking
**Solution:**
1. Check ngrok is running: `ngrok http 8000`
2. Check webhook URL in PayMongo dashboard
3. Check Django logs for errors
4. Verify task exists in database

### Issue: Webhook not received
**Solution:**
1. Verify ngrok URL is correct
2. Verify webhook URL in PayMongo dashboard
3. Check firewall settings
4. Try making payment again

### Issue: Payment shows but chat still locked
**Solution:**
1. Refresh page
2. Check database: `task.chat_unlocked`
3. Check logs for webhook confirmation
4. Contact support if issue persists

---

## 🎯 Expected Results

### After Payment
- ✅ Redirected to `/payment/success/`
- ✅ Message: "System fee payment successful!"
- ✅ Chat section shows message input
- ✅ Can send messages to task doer

### In Django Logs
```
🔔 PayMongo webhook received: payment.paid
💰 Payment received: ₱2.0 - Description: ErrandExpress System Fee - Task Title
Source ID: src_abc123xyz
📝 Processing as SYSTEM FEE payment
Extracted task_id: [your-task-id]
✅ System fee payment CONFIRMED - chat unlocked for task [your-task-id]
```

### In Database
```
Task.chat_unlocked = True
SystemCommission.status = 'paid'
SystemCommission.paid_at = [current timestamp]
Notification created for user
```

---

## 💡 Tips

1. **Use Test Mode**: PayMongo test mode doesn't charge real money
2. **Check Logs**: Django logs show exactly what's happening
3. **Verify Database**: Use Django shell to check payment status
4. **Test Multiple Times**: Try different amounts and payment methods
5. **Keep ngrok Running**: Don't close ngrok terminal during testing

---

## 🔗 Quick Links

- **Django Server**: http://127.0.0.1:8000
- **PayMongo Dashboard**: https://dashboard.paymongo.com
- **ngrok Dashboard**: http://localhost:4040 (while running)

---

## ✨ That's It!

Your payment system is now working with:
- ✅ Immediate chat unlock
- ✅ Webhook confirmation
- ✅ Robust error handling
- ✅ Detailed logging

**Ready to test!** 🚀
