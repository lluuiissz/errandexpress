import re
import os

file_path = r'core/templates/payments/commission_payment.html'

def check_file():
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex for split tags
    split_tag_pattern = re.compile(r'{%[^{}%]*\n[^{}%]*%}')
    split_var_pattern = re.compile(r'{{[^{}]*\n[^{}]*}}')

    errors = []
    
    def get_line_number(index, source):
        return source.count('\n', 0, index) + 1

    for match in split_tag_pattern.finditer(content):
        tag_content = match.group(0)
        # Filter out valid blocks if matched by accident, but standard logic should alert on any newline inside tag constraints.
        line = get_line_number(match.start(), content)
        errors.append(f"Line {line}: Multi-line tag found: {tag_content[:40]}...")

    for match in split_var_pattern.finditer(content):
        tag_content = match.group(0)
        line = get_line_number(match.start(), content)
        errors.append(f"Line {line}: Multi-line variable found: {tag_content[:40]}...")

    if errors:
        print(f"ℹ️ Found {len(errors)} potential issues in {os.path.basename(file_path)}:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"✅ No multi-line tags found in {os.path.basename(file_path)}")

if __name__ == "__main__":
    check_file()
