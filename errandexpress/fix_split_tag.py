import re

# Read the file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the split template tag on lines 302-303
# Replace the malformed multi-line tag with a single-line version
content = content.replace(
    '{% if conv.last_message.sender == user %}<span class="text-blue-600">You:</span> {%\r\n                                endif %}',
    '{% if conv.last_message.sender == user %}<span class="text-blue-600">You:</span> {% endif %}'
)

# Write back
with open('core/templates/messages/list.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed split template tag!")
