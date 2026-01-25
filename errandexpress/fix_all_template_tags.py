"""
Comprehensive template tag fixer for base_complete.html
Finds and fixes all broken Django template tags
"""

import re

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\base_complete.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 70)
print("SCANNING FOR BROKEN TEMPLATE TAGS")
print("=" * 70)

# Find all broken template tags (split across lines)
issues = []

for i, line in enumerate(lines, 1):
    # Check for incomplete template tags
    if '{%' in line and '%}' not in line:
        issues.append((i, 'incomplete_open', line.strip()))
    elif '%}' in line and '{%' not in line:
        issues.append((i, 'incomplete_close', line.strip()))
    
    # Check for broken endif specifically
    if 'Spent{%' in line or 'Earned{%' in line:
        issues.append((i, 'broken_endif', line.strip()))

print(f"\nFound {len(issues)} potential issues:\n")
for line_num, issue_type, line_content in issues:
    print(f"Line {line_num} ({issue_type}): {line_content[:80]}")

# Fix the specific known issue on line 673-674
print("\n" + "=" * 70)
print("APPLYING FIXES")
print("=" * 70)

# Fix broken endif tag
old_pattern = r"{% if user\.role == 'task_doer' %}Earned{% else %}Spent{%\s*endif %}"
new_pattern = r"{% if user.role == 'task_doer' %}Earned{% else %}Spent{% endif %}"

content_fixed = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE | re.DOTALL)

if content_fixed != content:
    print("✓ Fixed broken endif tag")
    
    # Write the fixed content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print("✓ File saved successfully")
    print("\n" + "=" * 70)
    print("TEMPLATE FIXED!")
    print("=" * 70)
    print("\nThe Django server should auto-reload.")
    print("Refresh your browser to see the fix.")
else:
    print("⚠ No changes made - pattern not found")
    print("\nSearching for the actual content...")
    
    # Search for the problematic lines
    for i, line in enumerate(lines, 1):
        if 'Spent' in line and 'task_doer' in line:
            print(f"\nLine {i}: {line}")
            if i < len(lines):
                print(f"Line {i+1}: {lines[i]}")

print("\n" + "=" * 70)
