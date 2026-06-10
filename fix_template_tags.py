
import re

file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\applications.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix Split Variable Tags {{ ... }}
# Matches {{ followed by anything (non-greedy), ending with }}
# DOMALL allows dot to match newlines
def join_tags(match):
    # Extract inner content
    inner = match.group(1)
    # Replace newlines and extra spaces with a single space
    clean_inner = ' '.join(inner.split())
    return f"{{{{ {clean_inner} }}}}"

content = re.sub(r'\{\{(.*?)\}\}', join_tags, content, flags=re.DOTALL)

# 2. Fix Split Block Tags {% ... %}
def join_blocks(match):
    inner = match.group(1)
    clean_inner = ' '.join(inner.split())
    # Preserving the type (e.g. {% if ... %})
    return f"{{% {clean_inner} %}}"

content = re.sub(r'\{%(.*?)%\}', join_blocks, content, flags=re.DOTALL)

# 3. Post-processing fixes (logic errors)
# Fix ' open' space
content = content.replace("task.status == ' open'", "task.status == 'open'")
# Fix joined tight equality
content = content.replace("task.status=='in_progress'", "task.status == 'in_progress'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully joined tags and fixed logic!")
