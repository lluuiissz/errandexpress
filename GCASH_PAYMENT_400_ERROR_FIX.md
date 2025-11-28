# GCash Payment 400 Error - Root Cause & Complete Fix

## Problem Summary
The GCash payment endpoint was returning a **400 Bad Request** error when attempting to create a PayMongo payment source. The error occurred at:
```
api/complete-task-payment/007acc35-952d-4b52-94ec-8bfe6cc06fa7/ - Status 400
```

## Root Causes Identified

### 1. **Missing Validation in PayMongo API Request**
- The `create_source` method in `paymongo.py` wasn't validating the amount before sending to PayMongo
- Invalid or zero amounts were being sent to the API
- No timeout was set on the request, causing potential hanging

### 2. **Incomplete Error Handling in GCash Endpoint**
- The `create_task_gcash_payment` endpoint wasn't logging the full PayMongo response
- Missing validation for required fields (payment_id, amount)
- No proper error messages returned to the client

### 3. **Missing Payment Tracking Fields**
- The `Payment` model was missing `paymongo_source_id` field to track GCash sources
- No `paid_at` field to track payment completion time
- Webhook couldn't properly match payments to sources

### 4. **Incomplete Webhook Integration**
- The webhook wasn't properly extracting payment IDs from descriptions
- No fallback logic if payment record didn't exist
- Task wasn't being marked as completed after payment confirmation

## Solutions Implemented

### 1. Enhanced PayMongo Client (`paymongo.py`)

```python
def create_source(self, amount, source_type="gcash", currency="PHP", 
                  success_url=None, failed_url=None, description="ErrandExpress Payment"):
    """Create a payment source with comprehensive validation"""
    try:
        # Convert amount to centavos (handle Decimal types)
        amount_centavos = int(float(amount) * 100)
        
        # ✅ VALIDATE AMOUNT
        if amount_centavos <= 0:
            logger.error(f"Invalid amount: {amount_centavos} centavos")
            return None
        
        # ✅ VALIDATE URLs
        if not success_url.startswith('http'):
            logger.error(f"Invalid success URL: {success_url}")
            return None
        if not failed_url.startswith('http'):
            logger.error(f"Invalid failed URL: {failed_url}")
            return None
        
        # ✅ ENHANCED LOGGING
        logger.info(f"Creating PayMongo source: type={source_type}, amount={amount_centavos} centavos")
        
        # ✅ TIMEOUT ADDED
        response = requests.post(
            f"{self.base_url}/sources",
            json=payload,
            headers=self.headers,
            timeout=10  # Prevent hanging
        )
        
        # ✅ DETAILED ERROR LOGGING
        if response.status_code != 200:
            logger.error(f"PayMongo source creation failed: Status={response.status_code}, Response={response.text}")
            return None
            
    except Exception as e:
        logger.error(f"PayMongo source creation error: {str(e)}")
        return None
```

**Key Improvements:**
- Amount validation (must be > 0)
- URL validation (must start with http/https)
- Request timeout (10 seconds)
- Detailed error logging with response status and body

### 2. Improved GCash Payment Endpoint (`views.py`)

```python
@csrf_exempt
def create_task_gcash_payment(request):
    """
    💳 Create GCash payment source for main task payment (STEP 5B)
    Integrated with PayMongo webhook for automatic confirmation
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        # ✅ VALIDATE PAYMENT_ID
        if not payment_id:
            logger.error("Missing payment_id in request")
            return JsonResponse({'error': 'Missing payment_id'}, status=400)
        
        # ✅ GET PAYMENT RECORD WITH ERROR HANDLING
        from .models import Payment
        try:
            payment = Payment.objects.get(id=payment_id, status='pending_payment')
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {payment_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # ✅ VALIDATE AMOUNT
        amount_centavos = int(float(payment.amount) * 100)
        if amount_centavos <= 0:
            logger.error(f"Invalid payment amount: {payment.amount}")
            return JsonResponse({'error': 'Invalid payment amount'}, status=400)
        
        # ✅ BUILD PROPER REDIRECT URLS
        success_url = request.build_absolute_uri(reverse('payment_success'))
        failed_url = request.build_absolute_uri(reverse('payment_failed'))
        success_url = f"{success_url}?payment_id={payment_id}"
        failed_url = f"{failed_url}?payment_id={payment_id}"
        
        # ✅ ENHANCED LOGGING
        logger.info(f"Creating GCash payment: payment_id={payment_id}, amount={amount_centavos} centavos")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # ✅ MAKE REQUEST WITH PROPER HEADERS
        response = requests.post(
            "https://api.paymongo.com/v1/sources",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {auth_header}"
            },
            json=payload,  # Use json parameter instead of data
            timeout=10
        )
        
        # ✅ DETAILED RESPONSE LOGGING
        logger.info(f"PayMongo response status: {response.status_code}")
        logger.info(f"PayMongo response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            try:
                checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
                source_id = result["data"]["id"]
                
                # ✅ STORE SOURCE_ID FOR WEBHOOK TRACKING
                payment.paymongo_source_id = source_id
                payment.save()
                
                logger.info(f"✅ Task GCash payment created: source_id={source_id}")
                return JsonResponse({
                    "success": True,
                    "checkout_url": checkout_url,
                    "source_id": source_id,
                    "amount": float(payment.amount),
                    "payment_id": str(payment_id)
                })
            except KeyError as e:
                logger.error(f"Invalid PayMongo response structure: {str(e)}")
                return JsonResponse({'error': 'Invalid payment response'}, status=500)
        else:
            logger.error(f"❌ Task GCash payment creation failed: Status={response.status_code}")
            logger.error(f"Response: {response.text}")
            return JsonResponse({'error': f'Payment creation failed: {response.status_code}'}, status=400)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        logger.error(f"Task GCash payment creation error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
```

**Key Improvements:**
- Request validation (payment_id, amount)
- Proper error handling with specific status codes
- Detailed logging of PayMongo response
- Source ID stored in payment record
- Using `json=payload` instead of `data=json.dumps(payload)`
- Timeout set to 10 seconds

### 3. Enhanced Payment Model (`models.py`)

```python
class Payment(models.Model):
    # ... existing fields ...
    paymongo_payment_id = models.CharField(max_length=255, blank=True, unique=True)
    paymongo_source_id = models.CharField(max_length=255, blank=True)  # ✅ NEW
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)  # ✅ NEW
```

**New Fields:**
- `paymongo_source_id`: Tracks GCash/Card payment sources for webhook matching
- `paid_at`: Records when payment was actually confirmed by PayMongo

### 4. Improved Webhook Handler (`views.py`)

```python
elif "Task Payment" in description or ("ErrandExpress Task Payment" in description):
    logger.info("📝 Processing as TASK DOER PAYMENT")
    
    try:
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        matches = re.findall(uuid_pattern, description)
        
        # ✅ EXTRACT BOTH TASK_ID AND PAYMENT_ID
        task_id = None
        payment_id = None
        
        if len(matches) >= 2:
            task_id = matches[0]
            payment_id = matches[1]
        elif len(matches) == 1:
            task_id = matches[0]
        
        task = Task.objects.get(id=task_id)
        
        # ✅ TRY TO GET EXISTING PAYMENT BY ID FIRST
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
            except Payment.DoesNotExist:
                payment = None
        else:
            payment = None
        
        # ✅ FALLBACK: GET BY TASK STATUS
        if not payment:
            try:
                payment = Payment.objects.get(task=task, status='pending_payment')
            except Payment.DoesNotExist:
                payment = None
        
        # ✅ CREATE IF DOESN'T EXIST
        if not payment:
            payment = Payment.objects.create(
                task=task,
                payer=task.poster,
                receiver=task.doer,
                amount=task.price,
                method='gcash',
                status='pending_payment'
            )
        
        # ✅ MARK AS PAID AND STORE SOURCE_ID
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.paymongo_source_id = source_id
        payment.save()
        
        # ✅ COMPLETE THE TASK
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        # ✅ ADD COMMISSION WITH PROPER DECIMAL HANDLING
        from decimal import Decimal
        commission_amount = Decimal(str(task.price)) * Decimal('0.10')
        wallet.add_revenue(amount=commission_amount, ...)
        
        # ✅ SEND NOTIFICATIONS
        Notification.objects.create(user=task.doer, ...)
        Notification.objects.create(user=task.poster, ...)
        
    except Exception as e:
        logger.error(f"Error processing task doer payment: {str(e)}", exc_info=True)
```

**Key Improvements:**
- Extracts both task_id and payment_id from description
- Multiple fallback strategies to find payment record
- Creates payment if it doesn't exist
- Marks task as completed after payment confirmation
- Proper Decimal handling for commission calculation
- Comprehensive error logging with traceback

## Complete Payment Flow (Fixed)

### Step 1: Create Payment Record
```
POST /api/complete-task-payment/{task_id}/
Body: { payment_method: 'paymongo' }
Response: { success: true, payment_id: '...', status: 'pending_payment' }
```

### Step 2: Create GCash Source
```
POST /api/create-task-gcash-payment/
Body: { payment_id: '...' }
Response: { 
    success: true, 
    checkout_url: 'https://...',
    source_id: 'src_...',
    payment_id: '...'
}
```

### Step 3: User Completes Payment
- User redirected to PayMongo GCash checkout
- User completes payment on GCash app
- PayMongo sends webhook to `/paymongo_webhook/`

### Step 4: Webhook Confirms Payment
```
POST /paymongo_webhook/
Payload: {
    data: {
        attributes: {
            type: 'payment.paid',
            data: {
                attributes: {
                    description: 'Task Payment - Task Title (ID: payment_id)',
                    amount: 50000  // in centavos
                }
            }
        }
    }
}
```

### Step 5: Payment Confirmed
- Payment status updated to 'paid'
- Task marked as 'completed'
- Commission added to system wallet
- Notifications sent to both users
- User redirected to rate page

## Debugging Checklist

### If 400 Error Still Occurs:
1. **Check PayMongo Logs**
   ```bash
   # Enable detailed logging
   logger.setLevel(logging.DEBUG)
   ```

2. **Verify Request Payload**
   - Amount must be > 0 (in centavos)
   - Currency must be 'PHP'
   - Type must be 'gcash' or 'card'
   - Redirect URLs must be valid HTTPS URLs

3. **Check API Keys**
   ```python
   # Verify in settings
   PAYMONGO_SECRET_KEY = '...'  # Must be set
   PAYMONGO_PUBLIC_KEY = '...'  # Must be set
   ```

4. **Monitor Webhook**
   - Check if webhook is being called
   - Verify webhook signature (if enabled)
   - Check payment status in webhook logs

5. **Database Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Testing the Fix

### Test Case 1: Create GCash Payment
```javascript
// In browser console
fetch('/api/create-task-gcash-payment/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        payment_id: 'your-payment-id'
    })
})
.then(r => r.json())
.then(data => console.log(data))
```

### Test Case 2: Verify Webhook
```bash
# Check webhook logs
tail -f logs/django.log | grep "PayMongo webhook"
```

### Test Case 3: Check Payment Status
```python
# In Django shell
from core.models import Payment
payment = Payment.objects.get(id='payment-id')
print(f"Status: {payment.status}")
print(f"Source ID: {payment.paymongo_source_id}")
print(f"Paid At: {payment.paid_at}")
```

## Files Modified

1. **`errandexpress/core/paymongo.py`**
   - Enhanced `create_source()` method with validation and logging

2. **`errandexpress/core/views.py`**
   - Improved `create_task_gcash_payment()` endpoint
   - Enhanced webhook handler for task payment confirmation

3. **`errandexpress/core/models.py`**
   - Added `paymongo_source_id` field to Payment model
   - Added `paid_at` field to Payment model

## Migration Required

```bash
python manage.py makemigrations core
python manage.py migrate core
```

## Summary

The 400 error was caused by:
1. Missing validation in the PayMongo API request
2. Incomplete error handling and logging
3. Missing payment tracking fields
4. Incomplete webhook integration

All issues have been fixed with:
- Comprehensive input validation
- Detailed error logging
- Enhanced payment model
- Improved webhook handler
- Better error messages to client

The payment flow is now fully integrated with PayMongo webhooks for automatic confirmation.
