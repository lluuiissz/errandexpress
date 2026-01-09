import re

# Read the file
with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the check_chat_access function
# Use regex to find the function and replace it

new_function = '''def check_chat_access(task_id, user):
    """
    🔒 SECURE CHAT ACCESS - COMMISSION REQUIRED BEFORE MESSAGING
    Checks if user can access chat for a specific task.
    
    NEW SECURE RULES:
    1. Commission MUST be paid before sending ANY messages
    2. No free messages - prevents bypass via contact info exchange
    3. After commission paid, unlimited chat
    4. Only poster and assigned doer can chat
    """
    try:
        task = Task.objects.select_related('poster', 'doer').get(id=task_id)
        
        # Only poster and assigned doer can chat
        if user not in [task.poster, task.doer]:
            return {'allowed': False, 'reason': 'Not authorized for this task'}
        
        # SECURITY: Require commission payment before ANY messages
        if not task.commission_deducted:
            from django.urls import reverse
            return {
                'allowed': False,
                'reason': f'Pay ₱{task.commission_amount} commission to unlock chat',
                'requires_payment': True,
                'commission_amount': task.commission_amount,
                'payment_url': reverse('payment_commission', args=[task.id])
            }
        
        # Commission paid - unlimited chat allowed
        return {
            'allowed': True,
            'commission_paid': True,
            'reason': 'Chat access granted (commission paid)'
        }
        
    except Task.DoesNotExist:
        return {'allowed': False, 'reason': 'Task not found'}'''

# Find the function using regex (from def to the next def or class)
pattern = r'def check_chat_access\(task_id, user\):.*?(?=\ndef |class |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Replace the old function with the new one
    content = content[:match.start()] + new_function + '\n\n' + content[match.end():]
    
    # Write back
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully replaced check_chat_access function!")
    print(f"Old function was {len(match.group())} characters")
    print(f"New function is {len(new_function)} characters")
else:
    print("❌ Could not find check_chat_access function")
