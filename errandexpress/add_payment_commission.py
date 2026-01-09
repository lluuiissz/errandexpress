# New payment_commission view function to add to views.py

new_view_function = '''
@login_required
def payment_commission(request, task_id):
    """
    Handle commission payment before chat unlock.
    User must pay 10% commission before sending first message.
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Only task poster can pay commission
    if task.poster != request.user:
        messages.error(request, "Only the task poster can pay the commission.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if already paid
    if task.commission_deducted:
        messages.info(request, "Commission already paid. Chat is unlocked.")
        return redirect('messages_chat', task_id=task_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'gcash')
        
        if payment_method == 'gcash':
            # Collect GCash payment info
            fullname = request.POST.get('fullname', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            gcash_number = request.POST.get('gcash_number', '').strip()
            
            # Validate required fields
            if not all([fullname, phone, email]):
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'payments/commission_payment.html', {
                    'task': task,
                    'commission_amount': task.commission_amount,
                    'doer_payment_amount': task.doer_payment_amount,
                    'fullname': fullname,
                    'phone': phone,
                    'email': email,
                    'gcash_number': gcash_number,
                    'payment_methods': [
                        {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
                        {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
                    ]
                })
            
            # Store payment info in session
            request.session['gcash_fullname'] = fullname
            request.session['gcash_phone'] = phone
            request.session['gcash_email'] = email
            request.session['gcash_number'] = gcash_number
            request.session['payment_task_id'] = str(task.id)
            request.session['payment_type'] = 'commission_payment'
            
            logger.info(f"Commission payment form submitted for task {task_id}")
            
            # Redirect to payment processing
            return redirect('payment_commission_process', task_id=task_id)
        
        elif payment_method == 'card':
            # Collect card payment info
            fullname = request.POST.get('fullname', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            
            # Validate required fields
            if not all([fullname, phone, email]):
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'payments/commission_payment.html', {
                    'task': task,
                    'commission_amount': task.commission_amount,
                    'doer_payment_amount': task.doer_payment_amount,
                    'fullname': fullname,
                    'phone': phone,
                    'email': email,
                    'payment_methods': [
                        {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
                        {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
                    ]
                })
            
            # Store payment info in session
            request.session['card_fullname'] = fullname
            request.session['card_phone'] = phone
            request.session['card_email'] = email
            request.session['payment_task_id'] = str(task.id)
            request.session['payment_type'] = 'commission_payment'
            
            logger.info(f"Commission card payment form submitted for task {task_id}")
            
            # Redirect to card payment processing
            return redirect('payment_commission_card', task_id=task_id)
    
    # Render payment form
    context = {
        'task': task,
        'commission_amount': task.commission_amount,
        'doer_payment_amount': task.doer_payment_amount,
        'doer': task.doer,
        'fullname': request.user.fullname or '',
        'email': request.user.email or '',
        'phone': request.user.phone_number or '',
        'payment_methods': [
            {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
            {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
        ]
    }
    return render(request, 'payments/commission_payment.html', context)
'''

# Find where to insert the new function (after payment_system_fee)
with open('core/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line number of payment_system_fee
insert_line = None
for i, line in enumerate(lines):
    if 'def payment_system_fee(request, task_id):' in line:
        # Find the end of this function (next def or class)
        for j in range(i+1, len(lines)):
            if lines[j].startswith('def ') or lines[j].startswith('class '):
                insert_line = j
                break
        break

if insert_line:
    # Insert the new function
    lines.insert(insert_line, new_view_function + '\n\n')
    
    # Write back
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Successfully added payment_commission function at line {insert_line}")
else:
    print("❌ Could not find insertion point")
