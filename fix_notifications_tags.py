
import re

file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\notifications\list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Split Variable Tags {{ ... }}
def join_tags(match):
    inner = match.group(1)
    clean_inner = ' '.join(inner.split())
    return f"{{{{ {clean_inner} }}}}"

# Use DOTALL to match across newlines
content = re.sub(r'\{\{(.*?)\}\}', join_tags, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed tags in {file_path}")
