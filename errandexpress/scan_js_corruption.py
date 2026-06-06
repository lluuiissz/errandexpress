
import os
import re

def scan_js_corruption(directory):
    print(f"Scanning directory: {directory} for JS corruption ({{) or (}})...")
    
    # Patterns to look for:
    # 1. {{)  -> should be (() or similar
    # 2. (}}  -> should be ()) or similar
    # 3. }} in weird places inside script tags
    
    corruption_pattern = re.compile(r'(\(\s*}}\s*|\{\{\s*\))')
    
    files_with_issues = []

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
            
            # Simple check first
            if '{{)' in content or '(}}' in content:
                print(f"POSSIBLE CORRUPTION in {file}")
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '{{)' in line or '(}}' in line:
                        print(f"  Line {i+1}: {line.strip()[:100]}")
                
                files_with_issues.append(path)

    print(f"\n--- SUMMARY ---")
    print(f"Files with potential JS corruption: {len(files_with_issues)}")
    for f in files_with_issues:
        print(f"- {f}")

if __name__ == '__main__':
    target_dir = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates'
    if os.path.exists(target_dir):
        scan_js_corruption(target_dir)
    else:
        print("Directory not found")
