# Read the file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the split tag on lines 399-401 (indices 398-400)
# Current state spans 3 lines, need to combine into 1

# Replace line 399 with the combined version
lines[398] = '                        <strong>{{ chat_access.messages_remaining }}</strong> free message{% if chat_access.messages_remaining != 1 %}s{% endif %} remaining. After 5 messages, 10% commission will be auto-deducted from task amount.\r\n'

# Delete lines 400 and 401 (now indices 399 and 400)
del lines[399]
del lines[399]  # After first delete, what was 401 is now at 399

# Write back
with open('core/templates/messages/list.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed split template tag on lines 399-401!")
print("Combined 3 lines into 1.")
