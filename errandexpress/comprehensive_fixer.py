#!/usr/bin/env python3
"""
COMPREHENSIVE TEMPLATE FIXER
Fixes specific Django template syntax errors globally:
1. Missing spaces around comparison operators (==, !=, >=, <=)
2. Split variable tags
3. Split block tags
"""

import os
import re

def fix_content(content):
    original_content = content
    changes = []

    # 1. Fix missing spaces around operators in if tags
    # Pattern: {% if variable==value %} -> {% if variable == value %}
    # We look for == inside {% ... %} blocks.
    # Regex explanation:
    # \{%               Match opening tag
    # [^%]*?            Match content lazily
    # (?<=[^\s!=<>])    Lookbehind: ensure preceding char is not space or operator part
    # (==|!=|>=|<=)     Match operator
    # (?=[^\s!=<>])     Lookahead: ensure following char is not space or operator part
    # [^%]*?            Match remaining content
    # %\}               Match closing tag
    
    # Since re.sub processing full blocks is safer than trying to parse everything, 
    # let's iterate over all {% if ... %} blocks and fix them individually.
    
    def fix_block(match):
        block_content = match.group(0)
        # Fix ==
        fixed = re.sub(r'(?<=[^\s!=<>])==(?=[^\s!=<>])', ' == ', block_content)
        # Fix !=
        fixed = re.sub(r'(?<=[^\s!=<>])!=(?=[^\s!=<>])', ' != ', fixed)
        # Fix >=
        fixed = re.sub(r'(?<=[^\s!=<>])>=(?=[^\s!=<>])', ' >= ', fixed)
        # Fix <=
        fixed = re.sub(r'(?<=[^\s!=<>])<=(?=[^\s!=<>])', ' <= ', fixed)
        
        if fixed != block_content:
            return fixed
        return block_content

    content = re.sub(r'\{%.*?%\}', fix_block, content, flags=re.DOTALL)

    # 2. Fix split variable tags {{ ... \n ... }}
    content = re.sub(
        r'\{\{\s*([^}]+?)\n\s*([^}]+?)\}\}',
        lambda m: '{{ ' + ' '.join(m.group(1, 2).split()) + ' }}',
        content,
        flags=re.MULTILINE
    )

    # 3. Fix split block tags (specific commonly broken ones)
    content = re.sub(r'\{%\s*endif\s*\n\s*%\}', '{% endif %}', content)
    content = re.sub(r'\{%\s*else\s*\n\s*%\}', '{% else %}', content)
    content = re.sub(
        r'\{%\s*elif\s*\n\s*([^%]+?)\s*%\}', 
        lambda m: f"{{% elif {m.group(1).strip()} %}}", 
        content,
        flags=re.MULTILINE
    )

    return content

def main():
    print("=" * 70)
    print("RUNNING COMPREHENSIVE TEMPLATE FIXER")
    print("=" * 70)
    
    root_dir = os.path.join(os.getcwd(), 'core', 'templates')
    fixed_count = 0
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.html'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = fix_content(content)
                    
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"🔧 Fixed issues in {filename}")
                        fixed_count += 1
                        
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")

    print("-" * 70)
    print(f"Total files fixed: {fixed_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
