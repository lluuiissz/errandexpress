
import os
import re

TEMPLATES_DIR = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates'

def scan_and_fix(content, filename):
    original_content = content
    modified = False
    
    # Pattern 1: corrupted "}}" in JS that should be "))" or ");"
    # Logic: If "}}" appears and is NOT part of a Django tag "{{ ... }}"
    # Django tags are {{ var }} or {{ var|filter }}
    # We really only care about "}}" appearing in <script> blocks or generally where it's invalid JS.
    # But doing this smartly is hard.
    # Let's look for specific known garbage like:
    # .remove('active'}}; -> .remove('active'));
    # .includes('foo'}}; -> .includes('foo'));
    # === (name + '='} -> === (name + '=')
    # substring(..., ...} -> substring(..., ...)
    # } {  <-- Likely garbage from bad merge
    
    # 1. Fix corrupted parens/braces at end of statements
    # Pattern: \(([^)]+)\}\} -> ($1))  (variables?)
    # Pattern: \('([^']+)'\}\} -> ('$1'))
    
    # Case: .classList.remove('active'}};
    content = re.sub(r"\.classList\.remove\('([^']+)'\}\};", r".classList.remove('\1'));", content)
    content = re.sub(r"\.classList\.add\('([^']+)'\}\};", r".classList.add('\1'));", content)
    
    # Case: .includes('foo'}};
    content = re.sub(r"\.includes\('([^']+)'\}\}", r".includes('\1'))", content)
    content = re.sub(r"\.includes\(([^)]+)\}\}", r".includes(\1))", content)
    
    # Case: Garbage line "} {" on its own line
    content = re.sub(r"^\s*\}\s*\{\s*$", "", content, flags=re.MULTILINE)
    
    # Case: corrupted substring end
    # .substring(name.length + 1} -> .substring(name.length + 1)
    content = re.sub(r"\.substring\(([^}]+)\}", r".substring(\1)", content)
    
    # Case: === (name + '='}
    content = re.sub(r"=== \(([^}]+)\}", r"=== (\1))", content)
    
    # Check for specific "markAllAsRead" definition issues?
    
    if content != original_content:
        return content
    return None

count = 0
for root, dirs, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixed_content = scan_and_fix(content, file)
            
            if fixed_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"Fixed JS corruption in {file}")
                count += 1

print(f"Finished. Fixed {count} files.")
