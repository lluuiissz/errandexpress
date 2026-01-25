"""
Find and fix ALL broken template tags in rate_user.html
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\ratings\rate_user.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 70)
print("SCANNING FOR ALL BROKEN TEMPLATE TAGS")
print("=" * 70)

# Find all lines with incomplete template tags
issues = []
for i, line in enumerate(lines, 1):
    # Check for {{ without }}
    if '{{' in line and '}}' not in line:
        issues.append((i, 'incomplete_open', line.strip()[:80]))
    # Check for }} without {{
    elif '}}' in line and '{{' not in line:
        issues.append((i, 'incomplete_close', line.strip()[:80]))

print(f"\nFound {len(issues)} broken template tags:\n")
for line_num, issue_type, line_content in issues:
    print(f"Line {line_num} ({issue_type}): {line_content}")

# Fix all broken tags
print("\n" + "=" * 70)
print("APPLYING FIXES")
print("=" * 70)

fixes_applied = 0

# Fix 1: rated_user.total_ratings|pluralize (around line 238)
old1 = '''<p class="text-xs text-gray-600 mt-1">({{ rated_user.total_ratings }} review{{
                                rated_user.total_ratings|pluralize }})</p>'''
new1 = '<p class="text-xs text-gray-600 mt-1">({{ rated_user.total_ratings }} review{{ rated_user.total_ratings|pluralize }})</p>'

if old1 in content:
    content = content.replace(old1, new1)
    print("✓ Fixed: rated_user.total_ratings|pluralize")
    fixes_applied += 1

# Write the fixed content
if fixes_applied > 0:
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ Applied {fixes_applied} fix(es)")
    print("✓ File saved successfully")
    print("\n" + "=" * 70)
    print("ALL TEMPLATE TAGS FIXED!")
    print("=" * 70)
else:
    print("\n⚠ No fixes applied - showing context around broken tags:")
    for line_num, issue_type, _ in issues[:3]:  # Show first 3 issues
        print(f"\nAround line {line_num}:")
        for i in range(max(0, line_num-3), min(len(lines), line_num+2)):
            print(f"  {i+1}: {lines[i]}")

print("\n" + "=" * 70)
