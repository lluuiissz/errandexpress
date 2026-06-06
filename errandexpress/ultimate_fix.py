#!/usr/bin/env python3
"""
ULTIMATE TEMPLATE FIXER
Fixes ALL template issues in ONE pass
"""

import re
from pathlib import Path

def ultimate_fix(content):
    """Fix everything in one comprehensive pass"""
    
    # 1. Fix URL tag spaces - CRITICAL
    content = re.sub(r"\{%\s*url\s+'\s+(\w+)'\s*", r"{% url '\1' ", content)
    
    # 2. Join split tags (lines 121-122, 172-173, 183-184)
    # Fix {{ on one line, content on next line
    content = re.sub(
        r'\{\{\s*\n\s*([^}]+?)\}\}',
        lambda m: '{{ ' + ' '.join(m.group(1).split()) + ' }}',
        content,
        flags=re.MULTILINE
    )
    
    # 3. Remove duplicate braces
    content = re.sub(r'\{\{\s*\{\{', '{{', content)
    content = re.sub(r'\}\}\s*\}\}', '}}', content)
    
    return content

def main():
    print("=" * 70)
    print("ULTIMATE TEMPLATE FIXER - ALL ISSUES IN ONE PASS")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    target_file = base_dir / 'core' / 'templates' / 'tasks' / 'applications.html'
    
    print(f"\n🔧 Fixing {target_file.name}...\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = ultimate_fix(content)
    
    if content != original:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed all issues in {target_file.name}")
    else:
        print(f"ℹ️  No changes needed")
    
    print(f"\n{'=' * 70}")
    print("✅ Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
