import os
import re

files_to_fix = [
    r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\browse_tasks_modern.html",
    r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\task_detail_modern.html",
    r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\messages\list.html",
    r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\applications.html"
]

def fix_split_tags(content):
    # Regex to capture split {{ ... }} and {% ... %}
    # Matches {{ or {% followed by content, newline, more content, ending with }} or %}
    # Flags: DOTALL allows . to match newlines for the inner content
    
    # 1. Variable Tags {{ ... }}
    # We look for {{ [^}]* \n [^}]* }}
    # But safer: match {{ followed by anything non-greedy, then }}
    # And check if it contains newline
    
    def replacer(match):
        text = match.group(0)
        if '\n' in text:
            # Join spaces
            clean = re.sub(r'\s+', ' ', text)
            print(f"  > Fixed: {text[:20]}...")
            return clean
        return text

    # Apply to variables
    content = re.sub(r'{{.*?}}', replacer, content, flags=re.DOTALL)
    
    # Apply to blocks
    content = re.sub(r'{%.*?%}', replacer, content, flags=re.DOTALL)
    
    return content

print("Running bulk template repair...")
for file_path in files_to_fix:
    if os.path.exists(file_path):
        print(f"Processing {os.path.basename(file_path)}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw = f.read()
            
            fixed = fix_split_tags(raw)
            
            if fixed != raw:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                print("  ✅ Saved changes.")
            else:
                print("  No split tags found (or regex mismatch).")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print(f"⚠️ File not found: {file_path}")
