
import os
import re

TEMPLATES_DIR = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates'

def deep_scan_and_fix():
    print("Starting Deep Codebase Global Health Check...")
    
    # 1. Regex for Split Tags (newlines inside {% ... %} or {{ ... }})
    # We want to merge them into single lines
    split_tag_pattern = re.compile(r'({%[^{}%]*)\n\s*([^{}%]*%})')
    
    # 2. Regex for Raw Code artifacts (like 'MARK_ALL_AS_READ_FIX)
    raw_code_patterns = [
        r'MARK_ALL_AS_READ_FIX',
        r'}\s*{',  # Garbage from bad merges
        r'\{\{\s*\)\s*\}', # {{ ) }} garbage?
        r'\.remove\([\'"]active[\'"]\}\};', # Specific JS corruption
    ]
    
    count_fixed = 0
    files_checked = 0
    
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                files_checked += 1
                path = os.path.join(root, file)
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # --- APPLY FIXES ---
                
                # Fix Split Tags (Iterative to catch multi-line splits)
                # We loop until no more changes happen
                while True:
                    new_content = split_tag_pattern.sub(r'\1 \2', content)
                    if new_content == content:
                        break
                    content = new_content
                
                # Fix Garbage JS '}}' patterns (Global Safe List)
                content = content.replace(".classList.remove('active'}};", ".classList.remove('active'));")
                content = content.replace(".classList.add('active'}};", ".classList.add('active'));")
                content = content.replace("=== (name + '='}", "=== (name + '=')")
                
                # Fix specific known garbage
                content = content.replace("} {", "") 
                
                # Fix Double Endif (naive check if they are identical lines next to each other?)
                # Probably safer to just rely on user report or manual tool for logic errors
                # But we can remove the specific one we just found if it persists? 
                # No, we already fixed it via tool.
                
                # Write back if changed
                if content != original_content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"[FIXED] {file}")
                    count_fixed += 1
                
                # --- REPORTING ONLY (Tag Balance) ---
                # Simple heuristic for open/close tags
                open_ifs = len(re.findall(r'{%\s*if\s+', content))
                close_ifs = len(re.findall(r'{%\s*endif\s*%}', content))
                
                # Note: 'elif' and 'else' don't change the balance
                
                if open_ifs != close_ifs:
                    print(f"[WARNING] {file}: unbalanced 'if' tags (open={open_ifs}, close={close_ifs})")

    print(f"Deep scan complete. Checked {files_checked} files. Fixed {count_fixed} files.")

if __name__ == '__main__':
    deep_scan_and_fix()
