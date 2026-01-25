"""
Fix payment API to allow payments for completed tasks
"""

views_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\views.py'

# Read the file
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("FIXING PAYMENT API STATUS CHECK")
print("=" * 70)

# Fix the status check to allow both in_progress and completed tasks
old_code = """        # Detailed validation with specific error messages
        if task.status != 'in_progress':
            logger.error(f"❌ Invalid task status: {task.status} (expected: in_progress)")
            return {
                'success': False, 
                'message': f'Task status is "{task.status}", not "in_progress". Cannot process payment.'
            }"""

new_code = """        # Detailed validation with specific error messages
        # Allow both 'in_progress' and 'completed' tasks for payment
        # - in_progress: Normal flow (task ongoing, payment for completion)
        # - completed: Rate-and-pay flow (task done, payment before rating)
        if task.status not in ['in_progress', 'completed']:
            logger.error(f"❌ Invalid task status: {task.status} (expected: in_progress or completed)")
            return {
                'success': False, 
                'message': f'Task status is "{task.status}". Payment can only be processed for in-progress or completed tasks.'
            }"""

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Fixed payment status validation")
    
    # Write back
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ File saved successfully")
    print("\n" + "=" * 70)
    print("PAYMENT API FIXED!")
    print("=" * 70)
    print("\nPayments can now be processed for completed tasks.")
    print("This allows the rate-and-pay flow to work correctly.")
else:
    print("⚠ Pattern not found - showing context...")
    lines = content.split('\n')
    for i in range(615, 625):
        print(f"Line {i+1}: {lines[i]}")

print("\n" + "=" * 70)
