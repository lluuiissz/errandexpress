import re
import sys

file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\task_detail_modern.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

issues_found = []

# Check for split template tags
for i, line in enumerate(lines, 1):
    # Check if line has opening {percent but no closing percent}
    if '{%' in line and '%}' not in line:
        issues_found.append(f"Line {i}: Split template tag (opening without closing):\n  {line.strip()}")
    
    # Check if line has opening double-brace but no closing double-brace
    if '{{' in line and '}}' not in line:
        issues_found.append(f"Line {i}: Split variable tag (opening without closing):\n  {line.strip()}")
    
    # Check for lines that start with closing tags (continuation of split tag)
    stripped = line.strip()
    if stripped.startswith('%}') or stripped.startswith('}}'):
        issues_found.append(f"Line {i}: Continuation of split tag:\n  {line.strip()}")

# Count if/endif balance
if_count = 0
endif_count = 0
elif_count = 0
else_count = 0

for i, line in enumerate(lines, 1):
    # Count if statements
    if_matches = re.findall(r'{%\s*if\s+', line)
    if_count += len(if_matches)
    
    # Count elif statements
    elif_matches = re.findall(r'{%\s*elif\s+', line)
    elif_count += len(elif_matches)
    
    # Count else statements
    else_matches = re.findall(r'{%\s*else\s*%}', line)
    else_count += len(else_matches)
    
    # Count endif statements
    endif_matches = re.findall(r'{%\s*endif\s*%}', line)
    endif_count += len(endif_matches)

# Print results
print("\n" + "=" * 60)
print("TEMPLATE VALIDATION REPORT")
print("=" * 60)

if issues_found:
    print("\n🔍 SPLIT TAG ISSUES FOUND:")
    for issue in issues_found:
        print(issue)
else:
    print("\n✅ No split tags detected")

print(f"\n📊 TAG STATISTICS:")
print(f"   Total lines scanned: {len(lines)}")
print(f"   {{% if %}} tags: {if_count}")
print(f"   {{% elif %}} tags: {elif_count}")
print(f"   {{% else %}} tags: {else_count}")
print(f"   {{% endif %}} tags: {endif_count}")

if if_count == endif_count:
    print(f"\n✅ BALANCED: {if_count} if/endif pairs match perfectly!")
else:
    print(f"\n⚠️  UNBALANCED: {if_count} if tags vs {endif_count} endif tags")
    print(f"   Difference: {abs(if_count - endif_count)} tag(s)")
    issues_found.append("Unbalanced if/endif")

print("=" * 60)

if issues_found:
    sys.exit(1)
else:
    print("\n✅ ALL CHECKS PASSED!")
