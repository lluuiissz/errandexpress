
import os
import re

def fix_js_corruption(directory):
    print(f"Scanning directory: {directory} for JS corruption to fix...")
    
    # Patterns to fix
    # We use regex to carefully target the corruptions
    
    replacements = [
        # (pattern, replacement)
        (r'requestAnimationFrame\{\{\)', 'requestAnimationFrame(()'),
        (r'setTimeout\{\{\)', 'setTimeout(()'),
        (r'setInterval\{\{\)', 'setInterval(()'),
        (r'\.click\(\}\}', '.click()'),
        (r'\.json\(\}\}', '.json()'),
        (r'\}\} \=\> \{', ') => {'), # For arrows that got mangled like {{) => {
        (r'\{\{\) \=\> \{', '(() => {'),
        (r'\(\{\{', '(('),
        (r'\}\}\)', '))'),
        (r'String\((.*?)\}\}', r'String(\1))'),  # String(id}} -> String(id))
        (r'toggleSidebar\((.*?)\}\}', r'toggleSidebar(\1))'),
        (r'addEventListener\((.*?), \(\) \=\> (.*?)\(.*?\}\}\;', r'addEventListener(\1, () => \2());'), # Fix click handlers
    ]

    # More generic fallbacks (careful with these)
    # {{) -> (()
    # (}} -> ())
    
    files_fixed = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.html'):
                continue
            
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue
            
            original_content = content
            new_content = content
            
            # Apply specific replacements first
            new_content = re.sub(r'requestAnimationFrame\{\{\)', 'requestAnimationFrame(()', new_content)
            new_content = re.sub(r'setTimeout\{\{\)', 'setTimeout(()', new_content)
            new_content = re.sub(r'setInterval\{\{\)', 'setInterval(()', new_content)
            
            # Fix mangled arrow functions
            # e.g. setTimeout{{) => 
            new_content = re.sub(r'setTimeout\{\{\)\s*=>', 'setTimeout(() =>', new_content)
            new_content = re.sub(r'requestAnimationFrame\{\{\)\s*=>', 'requestAnimationFrame(() =>', new_content)
            
            # Fix .click(}}
            new_content = re.sub(r'\.click\(\}\}', '.click()', new_content)
            
            # Fix .json(}}
            new_content = re.sub(r'\.json\(\}\}', '.json()', new_content)
            
            # Fix toggleSidebar(true}}
            new_content = re.sub(r'toggleSidebar\((true|false)\}\}', r'toggleSidebar(\1))', new_content)
            
            # Fix String(x}}
            new_content = re.sub(r'String\(([^)]*?)\}\}', r'String(\1))', new_content)
            
            # Fix .has(x}}
            new_content = re.sub(r'\.has\(([^)]*?)\}\}', r'.has(\1))', new_content)

            # Fix confirm(x}}
            new_content = re.sub(r'confirm\(([^)]*?)\}\}', r'confirm(\1))', new_content)

            # Fix specific patterns seen in logs
            # setTimeout{{) => location.reload(), 500);
            new_content = re.sub(r'setTimeout\{\{\)\s*=>', 'setTimeout(() =>', new_content)
            
            if new_content != original_content:
                print(f"Fixed corruption in {file}")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                files_fixed += 1

    print(f"\n--- SUMMARY ---")
    print(f"Files fixed: {files_fixed}")

if __name__ == '__main__':
    target_dir = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates'
    if os.path.exists(target_dir):
        fix_js_corruption(target_dir)
    else:
        print("Directory not found")
