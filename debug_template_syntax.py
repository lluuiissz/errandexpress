import re

def check_syntax(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Regex for tags
    tag_re = re.compile(r'{%\s*(\w+)(?:\s+.*?)?\s*%}')

    print(f"Checking {filename}...")
    
    for i, line in enumerate(lines):
        line_num = i + 1
        matches = tag_re.finditer(line)
        
        for match in matches:
            tag_name = match.group(1)
            
            if tag_name in ('if', 'for', 'block', 'with'):
                stack.append((tag_name, line_num))
                print(f"{line_num}: Push {tag_name} -> Stack: {[x[0] for x in stack]}")
            
            elif tag_name in ('endif', 'endfor', 'endblock', 'endwith'):
                if not stack:
                    print(f"ERROR at {line_num}: Found {tag_name} but stack is empty!")
                    return
                
                last_tag, last_line = stack[-1]
                expected_end = 'end' + last_tag
                
                if tag_name == expected_end:
                    stack.pop()
                    print(f"{line_num}: Pop {tag_name} (closes {last_tag} from {last_line}) -> Stack: {[x[0] for x in stack]}")
                else:
                    print(f"ERROR at {line_num}: Found {tag_name} but expected {expected_end} (to close {last_tag} from {last_line})")
                    return

    if stack:
        print(f"ERROR: End of file reached with open blocks: {stack}")
    else:
        print("Syntax check passed!")

if __name__ == "__main__":
    check_syntax(r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\task_detail_modern.html')
