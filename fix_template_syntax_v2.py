
import re
import os

def fix_template_syntax(file_path):
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Pattern 1: Fix broken/split tags like {% if ... %}selected{% endif %}
        # This handles cases where {% endif %} might be on a new line or split incorrectly
        # We'll use a specific regex for the issues we see in the select options
        
        # Regex to find the <option> lines with the specific if condition pattern
        # This looks for <option ... {% if condition %}selected{% endif %}>
        # It handles newlines inside the tag
        
        def replacement(match):
            full_match = match.group(0)
            value_part = match.group(1) # e.g. typing
            condition_part = match.group(2) # e.g. filter_form.category.value=='typing'
            
            # Fix spacing around ==
            if '==' in condition_part:
                left, right = condition_part.split('==', 1)
                condition_part = f"{left.strip()} == {right.strip()}"
            
            return f'<option value="{value_part}" {{% if {condition_part} %}}selected{{% endif %}}>'

        # Fix Category Options
        # Matches: <option value="typing" {% if filter_form.category.value=='typing' %}selected{% endif %}>
        # and variations with newlines
        
        pattern = re.compile(r'<option value="([^"]+)"\s*{%\s*if\s+([^%]+?)\s*%}\s*selected\s*{%\s*endif\s*%}\s*>', re.DOTALL)
        content = pattern.sub(replacement, content)
        
        # Additional pass to explicitly check for filter_form.category.value=='...' (no spaces)
        # and ensure spaces are added
        content = re.sub(r"filter_form\.category\.value=='([^']+)'", r"filter_form.category.value == '\1'", content)
        content = re.sub(r"filter_form\.sort_by\.value=='([^']+)'", r"filter_form.sort_by.value == '\1'", content)
        
        # Also handle double quotes if any
        content = re.sub(r'filter_form\.category\.value=="([^"]+)"', r'filter_form.category.value == "\1"', content)
        content = re.sub(r'filter_form\.sort_by\.value=="([^"]+)"', r'filter_form.sort_by.value == "\1"', content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully fixed syntax errors.")
            return True
        else:
            print("No changes needed or regex didn't match.")
            return False
            
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

if __name__ == "__main__":
    file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\browse_tasks_modern.html"
    if os.path.exists(file_path):
        fix_template_syntax(file_path)
    else:
        print(f"File not found: {file_path}")
