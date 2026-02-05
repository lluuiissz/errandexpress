import re
import sys

def verify_template(filepath):
    print(f"Verifying {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 1. Check for basic tag balance
    tags_to_check = ['if', 'for', 'block', 'with']
    stack = []
    
    tag_pattern = re.compile(r'{%\s*(\w+)')
    end_tag_pattern = re.compile(r'{%\s*end(\w+)\s*%}')

    errors = []

    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Check for start tags
        matches = tag_pattern.finditer(line)
        for match in matches:
            tag_name = match.group(1)
            if tag_name in tags_to_check:
                stack.append((tag_name, line_num))
            elif tag_name.startswith('end'):
                # This is handled by end_tag_pattern generally, but 'end' prefix capture
                pass

        # Check for end tags
        end_matches = end_tag_pattern.finditer(line)
        for match in end_matches:
            tag_name = match.group(1)
            if not stack:
                errors.append(f"Line {line_num}: Unexpected {{% end{tag_name} %}}")
            else:
                last_tag, last_line = stack[-1]
                if last_tag == tag_name:
                    stack.pop()
                else:
                    # Mismatch could be nested wrong or parsing error
                    # But if we found 'endif' and last was 'if', it matches.
                    # If last was 'for', it's an error.
                    if tag_name == last_tag:
                         stack.pop()
                    else:
                         errors.append(f"Line {line_num}: Found {{% end{tag_name} %}} but expected {{% end{last_tag} %}} (opened line {last_line})")

    if stack:
        for tag, line in stack:
             errors.append(f"Unclosed tag: {{% {tag} %}} opened on line {line}")

    # 2. Check for broken tags (split across lines or malformed)
    # Regex for opening brace without closing brace on same line, excluding valid multiline tags?
    # Django tags generally should be on one line, or at least the tag name should be immediate.
    
    # Check for `{%` at end of line
    for i, line in enumerate(lines):
        if line.strip().endswith('{%'):
             errors.append(f"Line {i+1}: Tag {{% seems to be split across lines")
        if line.strip().startswith('%}'):
             errors.append(f"Line {i+1}: Tag ends with %}} on new line, possible split tag")

    # 3. Check for raw code ({{ var }} that likely didn't render or was escaped)
    # This is hard to distinguish from valid documentation, but if we see `{{ variable }}` inside a specific context maybe.
    # User's concern: "broken line and raw codes".
    # We will look for `{{` followed by text that isn't a variable? No.
    # We will look for `{{` inside `{%` or vice versa?
    
    # Let's just output any suspicious patterns
    
    print("\n--- Syntax Verification Results ---")
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
    else:
        print("[SUCCESS] No obvious nesting errors found.")
        
    # Check specifically for the reported issue text
    if "Inactive{%" in content.replace(" ", ""): # Rough check
         print("[WARNING] Found potential merged text 'Inactive{%'")

if __name__ == "__main__":
    verify_template(r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\admin_dashboard_modern.html")
