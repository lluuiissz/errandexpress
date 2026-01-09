import re

# Read the template file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track template tags with detailed info
stack = []
errors = []
all_tags = []

print("=" * 80)
print("COMPLETE TEMPLATE TAG ANALYSIS")
print("=" * 80)

for i, line in enumerate(lines, 1):
    # Find all Django template tags
    tags = re.findall(r'{%\s*(\w+)(?:\s+.*?)?%}', line)
    
    for tag in tags:
        all_tags.append((i, tag, line.strip()[:80]))
        
        if tag in ['for', 'if', 'block', 'with']:
            stack.append((tag, i, line.strip()[:80]))
            print(f"  {i:4d}: OPEN  {tag:10s} - {line.strip()[:60]}")
            
        elif tag in ['endfor', 'endif', 'endblock', 'endwith']:
            expected = tag[3:]  # Remove 'end' prefix
            
            if not stack:
                error_msg = f"Line {i}: Unexpected {tag} with no opening tag"
                errors.append(error_msg)
                print(f"❌ {i:4d}: ERROR - {error_msg}")
                
            elif stack[-1][0] != expected:
                error_msg = f"Line {i}: Found {tag} but expected end{stack[-1][0]} (opened at line {stack[-1][1]})"
                errors.append(error_msg)
                print(f"❌ {i:4d}: ERROR - Found {tag}, expected end{stack[-1][0]}")
                print(f"         Opening was at line {stack[-1][1]}: {stack[-1][2]}")
                
            else:
                opening = stack.pop()
                print(f"  {i:4d}: CLOSE {tag:10s} - matches line {opening[1]}")
                
        elif tag in ['else', 'elif']:
            if not stack or stack[-1][0] != 'if':
                error_msg = f"Line {i}: {tag} without matching if (stack: {[t for t, _, _ in stack]})"
                errors.append(error_msg)
                print(f"❌ {i:4d}: ERROR - {tag} without matching if")
                print(f"         Current stack: {[(t, l) for t, l, _ in stack]}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Check for unclosed tags
if stack:
    print("\n⚠️  UNCLOSED TAGS:")
    for tag, line_num, line_content in stack:
        print(f"  Line {line_num}: {tag} - {line_content}")
        errors.append(f"Line {line_num}: Unclosed {tag}")

if errors:
    print(f"\n❌ FOUND {len(errors)} ERRORS:")
    for error in errors:
        print(f"  • {error}")
else:
    print("\n✅ No errors found! All tags are balanced.")

# Show context around line 437
print("\n" + "=" * 80)
print("CONTEXT AROUND LINE 437")
print("=" * 80)
for i in range(max(0, 436-10), min(len(lines), 436+10)):
    marker = ">>> " if i == 436 else "    "
    tags_in_line = re.findall(r'{%\s*(\w+)', lines[i])
    tag_str = f" [{', '.join(tags_in_line)}]" if tags_in_line else ""
    print(f"{marker}{i+1:4d}: {lines[i].rstrip()}{tag_str}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if errors:
    print("\nThe template has unbalanced tags. Common fixes:")
    print("1. Add missing {% endif %} or {% endfor %} tags")
    print("2. Remove extra {% else %} or {% elif %} tags")
    print("3. Check for split template tags across multiple lines")
    print("\nRun this script to see exactly where the issues are.")
