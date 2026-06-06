
import os
import re

TEMPLATES_DIR = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates'

def fix_split_tags(content, filename):
    original_content = content
    
    # Regex to find tags split across lines
    # We look for {% ... %} or {{ ... }} that contain a newline
    
    # Logic:
    # 1. Find all potential tags using a broad pattern that allows newlines
    # 2. Check if they actually contain a newline
    # 3. If so, replace newlines/multiple spaces with a single space
    
    # Pattern for block tags {% ... %}
    # We use non-greedy match .*? but with DOTALL mode (re.S) via the pattern or logic
    # But finding balanced braces with regex is hard.
    # However, Django templates usually don't nest {% inside {%
    
    # We'll use a callback replacer
    
    def replacer(match):
        text = match.group(0)
        if '\n' in text:
            # Normalize whitespace: replace sequences of whitespace (including newlines) with a single space
            # But we must be careful not to mess up string literals if they contain newlines? 
            # HTML templates usually don't have newlines in string literals inside tags commonly, 
            # but let's assume we just want to join the tag structure.
            # A safer approach for now: just replace newlines with spaces, then collapse spaces.
            new_text = re.sub(r'\s+', ' ', text)
            print(f"Fixed split tag in {filename}: {text[:20]}... -> {new_text[:20]}...")
            return new_text
        return text

    # Pattern: \{%[^%]*?%\}  matches {% ... %} non-greedily
    # but we need to match across lines.
    # [^%]* is dangerous if % is inside string. 
    # Better: (\{%|{{).*?(%\}|}}) but that's mixed.
    
    # Let's do block tags first
    # pattern = r'\{%.*?%\}' with DOTALL
    
    content = re.sub(r'\{%\s*.*?\s*%\}', replacer, content, flags=re.DOTALL)
    
    # Variable tags {{ ... }}
    content = re.sub(r'\{\{\s*.*?\s*\}\}', replacer, content, flags=re.DOTALL)
    
    return content

count = 0
for root, dirs, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = fix_split_tags(content, file)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {file}")
                count += 1

print(f"Finished. Fixed {count} files.")
