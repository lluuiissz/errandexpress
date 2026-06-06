import re
import os

def fix_template_file(file_path):
    print(f"Checking {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix multi-line tags {{ ... }} that might be broken across lines
    # This regex looks for {{ that starts, has newlines, and ends with }}
    # It replaces newlines and extra spaces within the tag with a single space
    fixed_content = re.sub(
        r'\{\{\s*([^}]+?)\s*\}\}', 
        lambda m: '{{ ' + ' '.join(m.group(1).split()) + ' }}', 
        content, 
        flags=re.DOTALL
    )

    # 2. Fix broken {% ... %} tags as well just in case
    fixed_content = re.sub(
        r'\{%\s*([^%]+?)\s*%\}', 
        lambda m: '{% ' + ' '.join(m.group(1).split()) + ' %}', 
        fixed_content, 
        flags=re.DOTALL
    )

    if content != fixed_content:
        print(f"Found and fixed multi-line tags in {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
    else:
        print(f"No issues found in {file_path}")

if __name__ == "__main__":
    target_file = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\browse_tasks_modern.html"
    if os.path.exists(target_file):
        fix_template_file(target_file)
    else:
        print("File not found.")
