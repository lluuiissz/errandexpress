
import re

file_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\browse_tasks_modern.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific problematic pattern: comparison without spaces inside django tags
# Pattern: something=='something' -> something == 'something'
# modifying specifically the category value checks

patterns = [
    ("filter_form.category.value=='typing'", "filter_form.category.value == 'typing'"),
    ("filter_form.category.value=='powerpoint'", "filter_form.category.value == 'powerpoint'"),
    ("filter_form.category.value=='graphics'", "filter_form.category.value == 'graphics'"),
    ("filter_form.category.value=='research'", "filter_form.category.value == 'research'"),
    ("filter_form.category.value=='other'", "filter_form.category.value == 'other'"),
]

for old, new in patterns:
    if old in content:
        content = content.replace(old, new)
        print(f"Fixed: {old}")
    else:
        print(f"Not found: {old}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template fix script completed.")
