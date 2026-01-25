
import re

file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\messages\list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex to match the specific split pattern including the newlines and indentation
# We look for: {{ conversations|length }} conversation{{ \s+ conversations|length|pluralize }}</p>
# Using \s+ to match newlines and spaces.

pattern = r'{{ conversations\|length }} conversation{{\s+conversations\|length\|pluralize }}</p>'
replacement = r'{{ conversations|length }} conversation{{ conversations|length|pluralize }}</p>'

new_content = re.sub(pattern, replacement, content)

if new_content == content:
    print("No match found for regex replacement.")
else:
    print("Match found and replaced.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
