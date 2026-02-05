import re
import os

def fix_template_syntax(file_path):
    print(f"Checking {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific issue: ==value without spaces
    # We look for == inside {% if ... %} tags and ensure spaces around it
    # Regex explanation:
    # 1. match {% if
    # 2. match anything until we hit ==
    # 3. match ==
    # 4. match anything until %}
    
    # Simpler approach: find any `==` inside a tag and ensure it has spaces
    # But for this specific error reported: `filter_form.category.value==value`
    
    new_content = content.replace("filter_form.category.value==value", "filter_form.category.value == value")
    new_content = new_content.replace("filter_form.sort_by.value==value", "filter_form.sort_by.value == value")
    
    # Also generic fix for `==` without spaces in Django tags
    # This might be risky if not careful, but `==` is usually safe to space out in templates
    # pattern = r'(?<=[^\s])==(?=[^\s])' # matches == preceded and followed by non-space
    # new_content = re.sub(pattern, ' == ', new_content)
    
    if content != new_content:
        print(f"Fixed syntax errors in {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"No syntax issues found in {file_path}")

if __name__ == "__main__":
    target_file = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\browse_tasks_modern.html"
    if os.path.exists(target_file):
        fix_template_syntax(target_file)
    else:
        print("File not found.")
