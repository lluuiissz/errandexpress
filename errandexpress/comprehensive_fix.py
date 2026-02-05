#!/usr/bin/env python3
"""
Comprehensive Template Fixer
Fixes ALL template issues in one pass
"""

import os
import re
from pathlib import Path

def fix_all_issues(content):
    """Fix all template issues"""
    original = content
    
    # 1. Fix URL tags with spaces
    content = re.sub(r"\{%\s*url\s+'\s+(\w+)'", r"{% url '\1'", content)
    content = re.sub(r"\{%\s*url\s+'(\w+)\s+'", r"{% url '\1'", content)
    
    # 2. Fix split tags (multi-line variable tags)
    # Fix {{ on one line, content on next
    content = re.sub(
        r'\{\{\s*\n\s*([^}]+?)\}\}',
        lambda m: '{{ ' + ' '.join(m.group(1).split()) + ' }}',
        content,
        flags=re.MULTILINE
    )
    
    # 3. Fix missing opening braces
    # Pattern: word.word|filter }} (missing {{)
    content = re.sub(
        r'(?<![\{])\b(app\.\w+(?:\.\w+)?(?:\|\w+(?::\d+)?)?)\s*\}\}',
        r'{{ \1 }}',
        content
    )
    
    return content, content != original

def main():
    print("=" * 70)
    print("COMPREHENSIVE TEMPLATE FIXER")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    # Focus on applications.html first
    target_file = templates_dir / 'tasks' / 'applications.html'
    
    print(f"\n🔧 Fixing {target_file.name}...\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content, was_fixed = fix_all_issues(content)
    
    if was_fixed:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Fixed: {target_file.name}")
    else:
        print(f"ℹ️  No changes needed: {target_file.name}")
    
    print(f"\n{'=' * 70}")
    print("✅ Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
