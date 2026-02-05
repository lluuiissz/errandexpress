
import os
import re

# Directory to scan
search_dir = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates'

# Regex to find: {% url ' spaces
# We want to replace "{% url ' " with "{% url '"
# Also handle double quotes just in case: "{% url " " -> "{% url ""
pattern = re.compile(r"({%\s*url\s+['\"])\s+([^'\"]+['\"])")

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Function to replace the match
    # Group 1 is "{% url '"
    # Group 2 is "view_name' ..." (we want to strip the leading space from view_name, but the regex above captures the space in the middle)
    
    # Simpler approach: straight string replacement for the specific common error
    # The error is {% url ' view_name'
    # We want to turn it into {% url 'view_name'
    
    new_content = re.sub(r"({%\s*url\s+['\"])\s+([a-zA-Z0-9_]+)", r"\1\2", content)

    if new_content != content:
        print(f"Fixing {file_path}...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Walk through directory
count = 0
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            if fix_file(path):
                count += 1

print(f"Fixed {count} files.")
