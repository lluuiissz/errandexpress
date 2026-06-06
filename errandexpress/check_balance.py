#!/usr/bin/env python3
"""
Balance Tags Fixer
Detects and helps fix unbalanced tags in templates.
"""
import re
import os

def check_balance(content, filename):
    # Stack for tags
    stack = []
    lines = content.split('\n')
    
    # Regex to find tags
    # We care about block tags: if, for, block, with, while (if using jinja extensions, but this is django)
    # Django tags that require closing:
    # if -> endif
    # for -> endfor
    # block -> endblock
    # with -> endwith
    # comment -> endcomment
    # autoescape -> endautoescape
    # filter -> endfilter
    # spaceless -> endspaceless
    # empty is part of for, elif/else part of if.
    
    tag_regex = re.compile(r'\{%\s*(\w+)')
    
    OPENING_TAGS = {'if', 'for', 'block', 'with', 'comment', 'autoescape', 'filter', 'spaceless'}
    CLOSING_TAGS = {
        'endif': 'if', 
        'endfor': 'for', 
        'endblock': 'block', 
        'endwith': 'with', 
        'endcomment': 'comment', 
        'endautoescape': 'autoescape',
        'endfilter': 'filter', 
        'endspaceless': 'spaceless'
    }
    
    errors = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        matches = list(re.finditer(r'\{%\s*(\w+)', line))
        
        for match in matches:
            tag_name = match.group(1)
            
            if tag_name in OPENING_TAGS:
                stack.append((tag_name, line_num))
            elif tag_name in CLOSING_TAGS:
                expected_open = CLOSING_TAGS[tag_name]
                if not stack:
                    errors.append(f"Line {line_num}: Found unused '{{% {tag_name} %}}' (no opening tag)")
                else:
                    last_open, last_line = stack.pop()
                    if last_open != expected_open:
                        errors.append(f"Line {line_num}: Found '{{% {tag_name} %}}' but expected closing for '{last_open}' (from line {last_line})")
    
    while stack:
        tag, line = stack.pop()
        errors.append(f"Line {line}: Unclosed '{{% {tag} %}}'")
        
    return errors

def main():
    target_file = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html'
    print(f"Checking {target_file} for balance...")
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        errors = check_balance(content, 'task_detail_modern.html')
        
        if errors:
            print("❌ BALANCING ERRORS FOUND:")
            for err in errors:
                print(err)
        else:
            print("✅ No balancing errors found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
