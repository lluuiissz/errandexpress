"""
Add missing check-payment-status API endpoint
"""

# First, add the view function to views.py
views_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\views.py'
urls_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\errandexpress\urls.py'

print("=" * 70)
print("ADDING CHECK-PAYMENT-STATUS API ENDPOINT")
print("=" * 70)

# Read views.py
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

# Add the view function after the paymongo_webhook function
view_function = '''

@csrf_exempt
def api_check_payment_status(request):
    """
    API endpoint to check payment status
    Used by JavaScript to poll payment status after GCash popup closes
    """
    from django.http import JsonResponse
    from .models import Payment
    
    payment_id = request.GET.get('payment_id')
    
    if not payment_id:
        return JsonResponse({
            'success': False,
            'error': 'payment_id parameter is required'
        }, status=400)
    
    try:
        payment = Payment.objects.get(id=payment_id)
        
        return JsonResponse({
            'success': True,
            'payment_id': str(payment.id),
            'status': payment.status,
            'amount': float(payment.amount),
            'method': payment.method,
            'task_id': str(payment.task.id) if payment.task else None,
            'created_at': payment.created_at.isoformat(),
            'updated_at': payment.updated_at.isoformat()
        })
        
    except Payment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Payment not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
'''

# Find a good place to insert (after paymongo_webhook)
if 'def paymongo_webhook(request):' in views_content:
    # Find the end of paymongo_webhook function
    webhook_pos = views_content.find('def paymongo_webhook(request):')
    # Find the next function definition after webhook
    next_func_pos = views_content.find('\ndef ', webhook_pos + 100)
    
    if next_func_pos > 0:
        views_content = views_content[:next_func_pos] + view_function + views_content[next_func_pos:]
        print("✓ Added api_check_payment_status view function")
        
        # Write back
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(views_content)
        print("✓ views.py updated")
    else:
        print("⚠ Could not find insertion point")
else:
    print("⚠ paymongo_webhook not found")

# Now add the URL route
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

# Add the URL pattern after api_confirm_cod_payment
url_pattern = "    path('api/check-payment-status/', views.api_check_payment_status, name='api_check_payment_status'),\n"

if 'api/check-payment-status/' not in urls_content:
    # Find the line with api_confirm_cod_payment
    if "api/confirm-cod-payment" in urls_content:
        lines = urls_content.split('\n')
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if 'api/confirm-cod-payment' in line:
                new_lines.append(url_pattern.rstrip())
        
        urls_content = '\n'.join(new_lines)
        
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(urls_content)
        
        print("✓ Added URL route for api_check_payment_status")
    else:
        print("⚠ Could not find insertion point in urls.py")
else:
    print("ℹ URL route already exists")

print("\n" + "=" * 70)
print("API ENDPOINT CREATED!")
print("=" * 70)
print("\nEndpoint: GET /api/check-payment-status/?payment_id=<uuid>")
print("Returns: JSON with payment status, amount, method, etc.")
print("\n" + "=" * 70)
