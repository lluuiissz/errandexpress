import os
import re

def fix_template_content(content, filename):
    original_content = content
    changes = []

    # 1. Fix {% if value==value %} (missing spaces around operators)
    # This regex looks for comparison operators (==, !=, >=, <=, >, <) without surrounding spaces inside {% if ... %}
    # It's a bit complex to safely capture just the operator context, so we'll target specific known patterns or general cases carefully.
    
    # Specific fix for the reported issue in browse_tasks_modern.html
    if "filter_form.category.value==value" in content:
        content = content.replace("filter_form.category.value==value", "filter_form.category.value == value")
        changes.append("Fixed missing spaces in 'filter_form.category.value == value'")

    # General pattern for == without spaces inside tags, but be careful not to break other things.
    # Safe approach: matching strict patterns seen in Django templates
    # Replace foo==bar with foo == bar
    # We use a pattern that matches {% if ... A==B ... %}
    # We will do a generic pass for comparison operators surrounded by non-space chars
    def replace_operators(match):
        full_tag = match.group(0)
        # Add spaces around ==, !=, >=, <= if missing
        # We assume 2-char ops first, then 1-char.
        # But for now, let's stick to == and != which are most common errors
        new_tag = re.sub(r'(?<=[^\s!=<>])(==|!=|>=|<=)(?=[^\s!=<>])', r' \1 ', full_tag)
        if new_tag != full_tag:
            return new_tag
        return full_tag

    # Apply to all tag blocks {% ... %}
    # content = re.sub(r'\{%.*?%\}', replace_operators, content, flags=re.DOTALL) 
    # The above is risky if it overlaps with other replacements. Let's stick to targeted regex for now.
    
    # 2. Fix split tags (newlines inside tags)
    # Fix split variable tags {{ ... \n ... }}
    # We match {{ followed by anything, including newlines, until }}
    # We collapse whitespace to single space
    def separate_lines_fix(match):
        inner = match.group(1)
        if '\n' in inner:
            cleaned = ' '.join(inner.split())
            return f"{{{{ {cleaned} }}}}"
        return match.group(0)

    # Note: verify this doesn't break pre-formatted text, but usually {{ }} variables shouldn't contain newlines spanning lines unless intentionally long filter chains.
    # Given the previous context, we want to fix accidental splits.
    
    # Fix {{ variable\n|filter }}
    # Regex: {{ [non-}]*?\n[non-}]*? }}
    content = re.sub(r'\{\{([^}]*?\n[^}]*?)\}\}', separate_lines_fix, content)

    # Fix split block tags {% ... \n ... %}
    # Specifically {% endif \n %} and {% else \n %} which were seen before
    content = re.sub(r'\{%\s*endif\s*\n\s*%\}', '{% endif %}', content)
    content = re.sub(r'\{%\s*else\s*\n\s*%\}', '{% else %}', content)
    content = re.sub(r'\{%\s*elif\s+([^%]+?)\n\s*%\}', lambda m: f"{{% elif {' '.join(m.group(1).split())} %}}", content)
    
    # 3. Fix duplicate braces {{ {{ ... }} }}
    if '{{ {{' in content:
        content = re.sub(r'\{\{\s*\{\{', '{{', content)
        content = re.sub(r'\}\}\s*\}\}', '}}', content)
        changes.append("Fixed duplicate braces {{ {{ ... }} }}")

    # 4. Fix split attribute values with tags inside (like in option value)
    # Detection of broken lines around `value="{{ value }}"` if it got split?
    # The previous error was `{% if ... %} \n ...`.
    # Let's clean up specific patterns if found.

    if content != original_content:
        return content, changes
    return None, None

def main():
    print("Starting Global Template Fixer...")
    root_dir = os.path.join(os.getcwd(), 'core', 'templates')
    
    fixed_files = 0
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.html'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content, changes = fix_template_content(content, filename)
                    
                    if new_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Fixed {filename}:")
                        for change in changes:
                            print(f"  - {change}")
                        if not changes: # If changes were regex based and not explicit append
                            print("  - Fixed regex patterns (split tags/lines)")
                        fixed_files += 1
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    print(f"Total files fixed: {fixed_files}")

if __name__ == "__main__":
    main()
