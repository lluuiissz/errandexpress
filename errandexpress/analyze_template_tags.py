import re

# Read the base_complete.html file
with open(r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\base_complete.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track all if/endif tags
if_stack = []
issues = []

for i, line in enumerate(lines, 1):
    # Find all {% if ... %} tags (but not {% endif %})
    if_matches = re.findall(r'{%\s*if\s+', line)
    elif_matches = re.findall(r'{%\s*elif\s+', line)
    else_matches = re.findall(r'{%\s*else\s*%}', line)
    endif_matches = re.findall(r'{%\s*endif\s*%}', line)
    
    # Add if tags to stack
    for _ in if_matches:
        if_stack.append(('if', i, line.strip()))
    
    # elif and else don't change stack depth
    for _ in elif_matches:
        if not if_stack:
            issues.append(f"Line {i}: elif without matching if: {line.strip()}")
    
    for _ in else_matches:
        if not if_stack:
            issues.append(f"Line {i}: else without matching if: {line.strip()}")
    
    # Remove if tags from stack for each endif
    for _ in endif_matches:
        if if_stack:
            if_stack.pop()
        else:
            issues.append(f"Line {i}: endif without matching if: {line.strip()}")

print(f"Total lines: {len(lines)}")
print(f"\nUnclosed if tags: {len(if_stack)}")
if if_stack:
    print("\nUnclosed if tags:")
    for tag_type, line_num, line_content in if_stack:
        print(f"  Line {line_num}: {line_content[:100]}")

print(f"\nOther issues: {len(issues)}")
if issues:
    for issue in issues:
        print(f"  {issue}")

# Check line 643 specifically
if len(lines) >= 643:
    print(f"\nLine 643 content:")
    print(f"  {lines[642].strip()}")
    
    # Show context around line 643
    print(f"\nContext around line 643:")
    for i in range(max(0, 640), min(len(lines), 650)):
        marker = ">>>" if i == 642 else "   "
        print(f"{marker} {i+1}: {lines[i].rstrip()}")
