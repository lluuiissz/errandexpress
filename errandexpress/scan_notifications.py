import re

file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\notifications\list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

issues_found = []

# Check for split template tags
for i, line in enumerate(lines, 1):
    if '{%' in line and '%}' not in line:
        issues_found.append(f"Line {i}: Split template tag")
    if '{{' in line and '}}' not in line:
        issues_found.append(f"Line {i}: Split variable tag")
    stripped = line.strip()
    if stripped.startswith('%}') or stripped.startswith('}}'):
        issues_found.append(f"Line {i}: Continuation of split tag")

# Count if/endif balance
if_count = sum(1 for line in lines if re.search(r'{%\s*if\s+', line))
endif_count = sum(1 for line in lines if re.search(r'{%\s*endif\s*%}', line))

print(f"\n{'='*60}")
print(f"NOTIFICATIONS TEMPLATE VALIDATION")
print(f"{'='*60}")
print(f"Lines scanned: {len(lines)}")
print(f"{% if %} tags: {if_count}")
print(f"{% endif %} tags: {endif_count}")

if issues_found:
    print(f"\n🔍 ISSUES FOUND:")
    for issue in issues_found:
        print(f"  - {issue}")
else:
    print(f"\n✅ No split tags detected")

if if_count == endif_count:
    print(f"✅ Balanced if/endif pairs")
else:
    print(f"⚠️  UNBALANCED: {if_count} if vs {endif_count} endif")
    issues_found.append("Unbalanced")

print(f"{'='*60}\n")
