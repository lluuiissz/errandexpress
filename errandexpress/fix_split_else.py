#!/usr/bin/env python3
"""
Fix Split Else Tag
Specific fix for the split {% else %} tag in applications.html
"""

import re
from pathlib import Path

def fix_split_else(content):
    """Fix {% \\n else %} pattern"""
    # This pattern matches {% followed by newline/spaces and then else %}
    # We replace it with {% else %}
    return re.sub(r'\{%\s*\n\s*else\s*%\}', '{% else %}', content)

def main():
    print("=" * 70)
    print("FIXING SPLIT ELSE TAG")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    target_file = base_dir / 'core' / 'templates' / 'tasks' / 'applications.html'
    
    print(f"\nProcessing {target_file.name}...\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_split_else(content)
    
    if content != original:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed split else tag in {target_file.name}")
    else:
        print(f"ℹ️  No split else tag found (or pattern didn't match)")
        # Debug: check what's there
        match = re.search(r'\{%\s*else', content)
        if match:
            print(f"Found partial match: {match.group(0)}")
    
    print(f"\n{'=' * 70}")
    print("✅ Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
