
import re

FILE_PATH = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html'

def check_structure():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Regex for tags
    # We care about: if, for, block, with, while (if any)
    # And their ends: endif, endfor, endblock, endwith
    # Also else, elif check for immediate parent
    
    tag_pattern = re.compile(r'{%\s*(if|for|block|with|while|endif|endfor|endblock|endwith|else|elif)\b')

    for i, line in enumerate(lines):
        lineno = i + 1
        matches = list(tag_pattern.finditer(line))
        
        for match in matches:
            tag = match.group(1)
            
            if tag in ['if', 'for', 'block', 'with']:
                stack.append((tag, lineno))
                print(f"{lineno}: Push {tag} (Stack depth: {len(stack)})")
            
            elif tag in ['endif', 'endfor', 'endblock', 'endwith']:
                if not stack:
                    print(f"ERROR at line {lineno}: Unexpected '{tag}', stack is empty")
                    return
                
                last_tag, start_line = stack.pop()
                expected_end = 'end' + last_tag
                
                if tag != expected_end:
                    # Mismatch!
                    print(f"ERROR at line {lineno}: Found '{tag}' but expected '{expected_end}' (matched start '{last_tag}' at line {start_line})")
                    return
                
                print(f"{lineno}: Pop {last_tag} (matched {start_line})")
                
            elif tag in ['else', 'elif']:
                if not stack:
                    print(f"ERROR at line {lineno}: '{tag}' without open block")
                    return
                
                # Verify parent is 'if' (or 'for' for 'else')
                parent = stack[-1][0]
                if parent not in ['if', 'for']:
                     print(f"ERROR at line {lineno}: '{tag}' inside '{parent}' block (line {stack[-1][1]})")

    if stack:
        print("\nFINAL ERROR: Unclosed tags remaining:")
        for tag, lineno in stack:
            print(f"  - '{tag}' opened at line {lineno}")
    else:
        print("\nSUCCESS: All tags balanced.")

if __name__ == '__main__':
    check_structure()
