"""
Comprehensive if/endif matcher to find the exact missing endif
"""
import re

file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track all if and endif with line numbers
if_stack = []  # Stack to track unclosed ifs
all_ifs = []
all_endifs = []

for i, line in enumerate(lines, 1):
    # Find if statements (but not elif)
    if_matches = re.findall(r'{%\s*if\s+', line)
    for match in if_matches:
        if_stack.append((i, line.strip()[:70]))
        all_ifs.append(i)
    
    # Find endif statements
    endif_matches = re.findall(r'{%\s*endif\s*%}', line)
    for match in endif_matches:
        all_endifs.append(i)
        if if_stack:
            if_stack.pop()

print("=" * 80)
print("IF/ENDIF STACK ANALYSIS")
print("=" * 80)
print("Total IF tags:", len(all_ifs))
print("Total ENDIF tags:", len(all_endifs))
print()

if if_stack:
    print("❌ UNCLOSED IF STATEMENTS:")
    print("-" * 80)
    for line_num, content in if_stack:
        print("Line", line_num, ":", content)
    print()
    print("The missing endif should be added after one of these if statements")
else:
    print("✅ All if statements are closed!")

print()
print("=" * 80)
print("ALL IF TAGS (first 15):")
for i in all_ifs[:15]:
    print("Line", i, ":", lines[i-1].strip()[:70])

print()
print("ALL ENDIF TAGS (first 15):")
for i in all_endifs[:15]:
    print("Line", i, ":", lines[i-1].strip()[:70])
