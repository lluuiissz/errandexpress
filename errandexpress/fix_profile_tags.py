
import re

path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\profile.html"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: The Role Display (Lines 44-45)
# Regex to match the multi-line broken tag for role
# It looks like: {% ... Task Doer{% \s+ else %} ...
# We replace it with the single line version.
pattern1 = r"{% if user\.role == 'task_poster' %}.*?Task Doer{%\s+else %}.*?{% endif %}"
replacement1 = "{% if user.role == 'task_poster' %}Task Poster{% elif user.role == 'task_doer' %}Task Doer{% else %}{{ user.role|title }}{% endif %}"

# Fix 2: The Rating Display (Lines 79-80)
# Matches {% if user_rating > 0 %}{{ user_rating }}{% else \s+ %}N/A{% endif %}
pattern2 = r"{% if user_rating > 0 %}{{ user_rating }}{% else\s+%}N/A{% endif %}"
replacement2 = "{% if user_rating > 0 %}{{ user_rating }}{% else %}N/A{% endif %}"

# Apply regex substitution
new_content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
new_content = re.sub(pattern2, replacement2, new_content, flags=re.DOTALL)

if content != new_content:
    print("Fixing broken tags...")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed!")
else:
    print("No matches found using regex. Dumping specific area to debug:")
    # Dump the area around "Task Doer" to see what's actually there
    start = content.find("Task Doer{%")
    if start != -1:
        print(f"DEBUG DATA: {repr(content[start:start+50])}")
    else:
        print("Could not find 'Task Doer{%' anchor.")
