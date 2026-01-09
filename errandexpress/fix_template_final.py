# Read the file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 302-303 by combining them
# Line 302 (index 301): contains the split tag start
# Line 303 (index 302): contains the split tag end

# Replace lines 301-302 with the fixed version
lines[301] = '                                {% if conv.last_message.sender == user %}<span class="text-blue-600">You:</span> {% endif %}{{ conv.last_message.message|truncatewords:6 }}\r\n'
# Remove line 302 since we combined it into 301
del lines[302]

# Write back
with open('core/templates/messages/list.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed! Combined lines 302-303 into a single line.")
