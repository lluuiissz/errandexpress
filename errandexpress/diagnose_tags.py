import re

# Read the file
with open('core/templates/messages/list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and show the exact content around line 300-310
lines = content.split('\n')
print("Checking lines 299-311:")
for i in range(299, 311):
    line = lines[i]
    # Check for Django tags
    if '{%' in line:
        tags = re.findall(r'{%\s*(\w+)', line)
        print(f"Line {i+1}: {tags} -> {repr(line[:80])}")
    else:
        print(f"Line {i+1}: (no tags) -> {repr(line[:60])}")

# Now let's manually count if/endif pairs in this section
print("\n=== Analyzing tag balance ===")
section = '\n'.join(lines[299:314])
ifs = len(re.findall(r'{%\s*if\s', section))
endifs = len(re.findall(r'{%\s*endif\s*%}', section))
print(f"{% if %} tags: {ifs}")
print(f"{% endif %} tags: {endifs}")
print(f"Balance: {'OK' if ifs == endifs else 'UNBALANCED'}")
