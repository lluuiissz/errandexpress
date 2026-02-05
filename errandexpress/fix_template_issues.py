import os
import re

def fix_template_issues(directory):
    print(f"Scanning directory: {directory}")
    
    # Regex patterns
    # 1. Fix missing spaces around == in if tags
    # Matches {% if something==something %}
    missing_spaces_pattern = r'({%\s*if\s+[^%]+?)([^\s=])==([^\s=])([^%]*?%})'
    
    # 2. Fix split tags (simple case: {% ... \n ... %})
    # This is tricky with regex, doing line-by-line might be safer or reading whole file
    
    files_fixed = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix 1: Add spaces around ==
                # We simply find '==', check if surrounded by spaces.
                # Actually, let's just target the specific known bad patterns first to be safe, 
                # then general.
                
                # Specific fixes for the reported error
                content = content.replace('filter_form.category.value==value', 'filter_form.category.value == value')
                content = content.replace('filter_form.sort_by.value==value', 'filter_form.sort_by.value == value')
                
                # General fix for == inside {% %}
                def replace_eq(match):
                    return f"{match.group(1)}{match.group(2)} == {match.group(3)}{match.group(4)}"
                
                # Iterate until no more matches (to handle multiple ==)
                # But standard replace is safer for now.
                
                # Fix 2: Join split tags
                # Look for {% or {{ that is followed by newline before %} or }}
                # Pattern: ({%|{{)[^%}]*?\n[^%}]*(%}|}})
                # Note: This might be dangerous if meaningful newlines exist, but usually not inside tags.
                
                def join_tag(match):
                    tag_content = match.group(0)
                    # Replace newlines and extra spaces with single space
                    cleaned = re.sub(r'\s+', ' ', tag_content)
                    return cleaned

                # Regex for split tags
                content = re.sub(r'({%|{{)[^%}]*?\n[^%}]*?(%}|}})', join_tag, content, flags=re.DOTALL)

                # Fix 3: Fix the specific weird option tag split
                # <option value="{{ value }}" {% if ... %}selected{% endif
                #    %}>
                content = re.sub(r'(%}\s*selected\s*{%\s*endif)\s*\n\s*%}>', r'\1 %}>', content)
                # Wait, the split might be: ...{% endif \n ...
                
                # Let's fix the specific lines in browse_tasks_modern.html aggressively
                # Join lines 135-136 type splits
                content = re.sub(r'(selected{%\s*endif)\s*\n\s*%}>', r'\1 %}>', content)

                if content != original_content:
                    print(f"Fixing issues in {file}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_fixed += 1

    print(f"Total files fixed: {files_fixed}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fix_template_issues(base_dir)
