
import re

def check_nesting():
    file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    balance = 0
    stack = []
    
    for i, line in enumerate(lines, 1):
        # Find all tags in order
        tags = re.finditer(r'{%\s*(if|endif)\s*(.*?)%}', line)
        
        for match in tags:
            tag_type = match.group(1)
            content = match.group(0)
            print(f"Line {i}: {content.strip()} (Type: {tag_type})")
            
            if tag_type == 'if':
                balance += 1
                stack.append((i, content))
            elif tag_type == 'endif':
                balance -= 1
                if balance < 0:
                    print(f"❌ ERROR: Unmatched ENDIF at line {i}")
                    print(f"   Content: {content.strip()}")
                    return
                stack.pop()
                
    if balance > 0:
        print(f"❌ ERROR: Unclosed IF blocks at end. Balance: {balance}")
        for i, content in stack:
            print(f"   Line {i}: {content.strip()}")
    elif balance == 0:
        print("✅ SUCCESS: All blocks balanced.")

if __name__ == "__main__":
    check_nesting()
