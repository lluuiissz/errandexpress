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
            stack.append((tag, i, line.strip()[:80]))
        elif tag in ['endfor', 'endif', 'endblock', 'endwith']:
            expected = tag[3:]  # Remove 'end' prefix
            if not stack:
                errors.append(f"Line {i}: Unexpected {tag} with no opening tag")
                print(f"ERROR: Line {i} has {tag} but no opening tag")
            elif stack[-1][0] != expected:
                errors.append(f"Line {i}: Found {tag} but expected end{stack[-1][0]}")
                print(f"ERROR at line {i}:")
                print(f"  Found: {tag}")
                print(f"  Expected: end{stack[-1][0]}")
                print(f"  Opening was at line {stack[-1][1]}: {stack[-1][2]}")
                print()
            else:
                stack.pop()
        elif tag in ['else', 'elif']:
            # These should be inside an if block
            if not stack or stack[-1][0] != 'if':
                print(f"ERROR at line {i}: {tag} without matching if")
                print(f"  Current stack: {[(t, l) for t, l, _ in stack]}")
                print()

# Show unclosed tags
if stack:
    print("\nUNCLOSED TAGS:")
    for tag, line_num, line_content in stack:
        print(f"  Line {line_num}: {tag} - {line_content}")

# Show context around line 436
print("\n=== Context around line 436 ===")
for i in range(max(0, 425), min(len(lines), 445)):
    marker = ">>> " if i == 435 else "    "
    tags_in_line = re.findall(r'{%\s*(\w+)', lines[i])
    tag_str = f" [{', '.join(tags_in_line)}]" if tags_in_line else ""
    print(f"{marker}{i+1}: {lines[i].rstrip()}{tag_str}")
