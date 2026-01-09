import re

# Read the template file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track template tags
stack = []
errors = []

for i, line in enumerate(lines, 1):
    # Find all Django template tags
    tags = re.findall(r'{%\s*(\w+)(?:\s+.*?)?%}', line)
    
    for tag in tags:
        if tag in ['for', 'if', 'block', 'with']:
            stack.append((tag, i, line.strip()))
        elif tag in ['endfor', 'endif', 'endblock', 'endwith']:
            expected = tag[3:]  # Remove 'end' prefix
            if not stack:
                errors.append(f"Line {i}: Unexpected {tag} with no opening tag")
            elif stack[-1][0] != expected:
                errors.append(f"Line {i}: Found {tag} but expected end{stack[-1][0]} (opened at line {stack[-1][1]})")
                print(f"ERROR at line {i}:")
                print(f"  Current line: {line.strip()}")
                print(f"  Expected: end{stack[-1][0]}")
                print(f"  Found: {tag}")
                print(f"  Opening tag was at line {stack[-1][1]}: {stack[-1][2]}")
                print()
            else:
                stack.pop()

# Check for unclosed tags
if stack:
    print("UNCLOSED TAGS:")
    for tag, line_num, line_content in stack:
        print(f"  Line {line_num}: {tag} - {line_content}")
    print()

if errors:
    print("ERRORS FOUND:")
    for error in errors:
        print(f"  {error}")
else:
    print("No errors found!")

# Show context around line 314
print("\nContext around line 314:")
for i in range(max(0, 313-10), min(len(lines), 313+10)):
    marker = ">>> " if i == 313 else "    "
    print(f"{marker}{i+1}: {lines[i].rstrip()}")
