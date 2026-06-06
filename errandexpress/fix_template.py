import re

# Read the file
file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\browse_tasks_modern.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the template syntax errors
# Pattern 1: value==value with split endif
content = re.sub(
    r'{% if filter_form\.category\.value==value %}selected{% endif\s+%}>',
    r'{% if filter_form.category.value == value %}selected{% endif %}>',
    content
)

# Pattern 2: sort_by value==value with split endif
content = re.sub(
    r'{% if filter_form\.sort_by\.value==value %}selected{% endif\s+%}>',
    r'{% if filter_form.sort_by.value == value %}selected{% endif %}>',
    content
)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Template syntax fixed!")
print("Fixed patterns:")
print("  - filter_form.category.value==value → filter_form.category.value == value")
print("  - filter_form.sort_by.value==value → filter_form.sort_by.value == value")
