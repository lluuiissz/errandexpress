import re

path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\task_detail_modern.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Split IF tag
# Matches: {% if ... and [newline/spaces] existing_payment.method ... %}
pattern_if = r'{%\s*if existing_payment and existing_payment\.status == \'pending_confirmation\' and\s+existing_payment\.method == \'cod\'\s*%}'
replacement_if = "{% if existing_payment and existing_payment.status == 'pending_confirmation' and existing_payment.method == 'cod' %}"

# Pattern 2: Split Variable
# Matches: ... from {{ [newline/spaces] task.poster.fullname }}
pattern_var = r'from {{\s+task\.poster\.fullname\s*}}\?'
replacement_var = "from {{ task.poster.fullname }}?"

new_content = re.sub(pattern_if, replacement_if, content)
new_content = re.sub(pattern_var, replacement_var, new_content)

if new_content != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced content!")
else:
    print("No matches found. Regex might need adjustment.")
    # Debug: print snippet around line 324
    lines = content.splitlines()
    if len(lines) > 324:
        print("Line 324:", lines[323])
        print("Line 325:", lines[324])
