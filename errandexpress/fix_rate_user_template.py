"""
Fix the broken template tag in rate_user.html
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\ratings\rate_user.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("FIXING BROKEN TEMPLATE TAG IN RATE_USER.HTML")
print("=" * 70)

# Fix the broken template tag
# The tag is split across lines like this:
# <span class="...">{{
#     task.get_category_display }}</span>

old_pattern = '''<span
                                    class="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">{{
                                    task.get_category_display }}</span>'''

new_pattern = '<span class="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">{{ task.get_category_display }}</span>'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✓ Found and fixed the broken template tag")
    
    # Write back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ File saved successfully")
    print("\n" + "=" * 70)
    print("TEMPLATE FIXED!")
    print("=" * 70)
    print("\nRefresh your browser to see the category display correctly.")
else:
    print("⚠ Pattern not found - searching for similar patterns...")
    
    # Show lines around line 45
    lines = content.split('\n')
    for i in range(40, min(50, len(lines))):
        print(f"Line {i+1}: {lines[i]}")

print("\n" + "=" * 70)
