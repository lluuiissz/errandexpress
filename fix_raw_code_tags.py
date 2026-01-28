
import re
import os

def fix_broken_tags(file_paths):
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"Processing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Regex to find split variable tags {{ ... }} containing newlines
            # Captures content between {{ and }}
            pattern = re.compile(r'\{\{(?:\s|\n)+([^}]+?)(?:\s|\n)+\}\}', re.DOTALL)
            
            def replacement(match):
                inner_content = match.group(1).strip()
                # Remove excessive internal newlines/spaces if any, typically just one variable or filter chain
                clean_content = re.sub(r'\s+', ' ', inner_content)
                return f"{{{{ {clean_content} }}}}"
            
            new_content = pattern.sub(replacement, content)
            
            if new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Successfully fixed broken tags in {os.path.basename(file_path)}")
            else:
                print(f"No broken tags found in {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    files_to_fix = [
        r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\signup_modern.html"
    ]
    fix_broken_tags(files_to_fix)
