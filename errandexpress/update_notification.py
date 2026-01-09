# Update the notification message in handle_task_creation_with_payment

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the old notification message
old_message = "First 5 messages FREE. Commission: ₱{commission_amount} (10%). Doer receives: ₱{doer_receives}."
new_message = "Pay ₱{commission_amount} commission to unlock chat. Doer will receive ₱{doer_receives} upon completion."

content = content.replace(old_message, new_message)

# Write back
with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated notification message!")
