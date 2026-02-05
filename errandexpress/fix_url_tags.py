#!/usr/bin/env python3
"""
URL Tag Auto-Fixer
Automatically fixes spaces in Django URL tags
"""

import os
import re
from pathlib import Path

def fix_url_tags(content):
    """Fix URL tags with spaces"""
    original = content
    
    # Pattern 1: Fix space after opening quote in {% url ' name' %}
    content = re.sub(
        r"\{%\s*url\s+'\s+(\w+)'",
        r"{% url '\1'",
        content
    )
    
    # Pattern 2: Fix space before closing quote in {% url 'name ' %}
    content = re.sub(
        r"\{%\s*url\s+'(\w+)\s+'",
        r"{% url '\1'",
        content
    )
    
    return content, content != original

def main():
    print("=" * 70)
    print("URL TAG AUTO-FIXER")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    templates = list(templates_dir.rglob('*.html'))
    print(f"\n🔧 Fixing URL tags in {len(templates)} templates...\n")
    
    fixed_count = 0
    for template in sorted(templates):
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content, was_fixed = fix_url_tags(content)
        
        if was_fixed:
            with open(template, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed: {template.name}")
            fixed_count += 1
    
    print(f"\n{'=' * 70}")
    if fixed_count == 0:
        print("✅ No URL tag errors found!")
    else:
        print(f"✅ Fixed {fixed_count} file(s)")
    print("=" * 70)

if __name__ == '__main__':
    main()
