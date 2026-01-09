
import re

file_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\browse_tasks_modern.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []

for i, line in enumerate(lines):
    line_num = i + 1
    
    # Simple regex to find tags
    # We are looking for if, for, block, with
    tags = re.findall(r'{%\s*(if|for|block|with|while)\s+.*?\s*%}|{%\s*(endif|endfor|endblock|endwith|endwhile)\s*%}', line)
    
    for tag in tags:
        # tag is a tuple because of groups, join it or just check
        t = tag[0] or tag[1] # one of them will be non-empty
        
        if t in ['if', 'for', 'block', 'with', 'while']:
            stack.append((t, line_num))
            # print(f"Lines {line_num}: Opened {t}")
        elif t in ['endif', 'endfor', 'endblock', 'endwith', 'endwhile']:
            if not stack:
                print(f"ERROR Line {line_num}: Unexpected {t} (stack empty)")
                continue
            
            last_op, last_line = stack[-1]
            expected_close = 'end' + last_op
            
            if t == expected_close:
                stack.pop()
                # print(f"Line {line_num}: Closed {last_op} from line {last_line}")
            else:
                print(f"ERROR Line {line_num}: Mismatched {t}. Expected {expected_close} for {last_op} from line {last_line}")

if stack:
    print("\nUNCLOSED TAGS:")
    for op, line_num in stack:
        print(f"Line {line_num}: Unclosed {op}")
else:
    print("\nAll tags balanced.")
