
import re
import os

# Target file: base_complete.html
file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\base_complete.html'

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find split {{ variable }} tags
# It looks for {{ followed by non-closing-braces (including newlines) then }}
# We replace it with a single line version
def join_tags(match):
    inner = match.group(1)
    # Remove newlines and extra spaces, normalize to single spaces
    clean_inner = ' '.join(inner.split())
    return f"{{{{ {clean_inner} }}}}"

# Apply fix for variable tags
new_content = re.sub(r'\{\{(.*?)\}\}', join_tags, content, flags=re.DOTALL)

# Apply fix for block tags if any {% ... %}
def join_block_tags(match):
    inner = match.group(1)
    clean_inner = ' '.join(inner.split())
    return f"{{% {clean_inner} %}}"

new_content = re.sub(r'\{%(.*?)%\}', join_block_tags, new_content, flags=re.DOTALL)

# Write back
if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Fixed tags in {file_path}")
else:
    print(f"No changes made to {file_path}")
