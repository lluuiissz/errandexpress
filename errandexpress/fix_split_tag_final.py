# Read the file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the split tag on lines 302-303 (indices 301-302)
# Current state:
# Line 302: "{% if conv.last_message.sender == user %}<span class="text-blue-600">You:</span> {%"
# Line 303: "endif %}{{ conv.last_message.message|truncatewords:6 }}"

# Replace line 302 with the combined version
lines[301] = '                                {% if conv.last_message.sender == user %}<span class="text-blue-600">You:</span> {% endif %}{{ conv.last_message.message|truncatewords:6 }}\r\n'

# Delete line 303 (now index 302) since we combined it
del lines[302]

# Also need to remove the blank line 304 that will now be 303
if lines[302].strip() == '':
    del lines[302]

# Write back
with open('core/templates/messages/list.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed split template tag on lines 302-303!")
print("Removed 2 lines and combined them into one.")
