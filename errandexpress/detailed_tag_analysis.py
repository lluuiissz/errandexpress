import re

# Read the file
with open(r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\base_complete.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Count all if and endif tags
if_pattern = r'{%\s*if\s+'
endif_pattern = r'{%\s*endif\s*%}'

if_count = len(re.findall(if_pattern, content))
endif_count = len(re.findall(endif_pattern, content))

print(f"Total if tags: {if_count}")
print(f"Total endif tags: {endif_count}")
print(f"Difference: {if_count - endif_count}")

# Find all if and endif positions
if_positions = [(m.start(), 'if') for m in re.finditer(if_pattern, content)]
endif_positions = [(m.start(), 'endif') for m in re.finditer(endif_pattern, content)]

# Combine and sort
all_tags = sorted(if_positions + endif_positions, key=lambda x: x[0])

# Convert positions to line numbers
def pos_to_line(pos):
    return content[:pos].count('\n') + 1

print("\nAll if/endif tags in order:")
depth = 0
for pos, tag_type in all_tags:
    line_num = pos_to_line(pos)
    line_content = lines[line_num - 1].strip()
    
    if tag_type == 'if':
        print(f"  {'  ' * depth}Line {line_num}: {tag_type} - {line_content[:80]}")
        depth += 1
    else:
        depth -= 1
        print(f"  {'  ' * depth}Line {line_num}: {tag_type} - {line_content[:80]}")
    
    if depth < 0:
        print(f"    ERROR: endif without matching if!")
        depth = 0

if depth > 0:
    print(f"\nERROR: {depth} unclosed if tag(s)")
