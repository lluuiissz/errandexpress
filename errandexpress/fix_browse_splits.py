#!/usr/bin/env python3
"""
Fix all split tags in browse_tasks_modern.html
"""

import re
from pathlib import Path

def fix_all_split_tags(content):
    """Fix all patterns of split tags"""
    
    # Pattern 1: Fix split variable tags {{ ... \n ... }}
    content = re.sub(
        r'\{\{\s*([^}]+?)\n\s*([^}]+?)\}\}',
        lambda m: '{{ ' + ' '.join(m.group(1, 2).split()) + ' }}',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 2: Fix split endif tags {% endif \n %}
    content = re.sub(
        r'\{%\s*endif\s*\n\s*%\}',
        '{% endif %}',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 3: Fix split else tags {% \n else %}
    content = re.sub(
        r'\{%\s*\n\s*else\s*%\}',
        '{% else %}',
        content,
        flags=re.MULTILINE
    )
    
    return content

def main():
    print("=" * 70)
    print("FIXING ALL SPLIT TAGS IN BROWSE_TASKS_MODERN.HTML")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    target_file = base_dir / 'core' / 'templates' / 'browse_tasks_modern.html'
    
    print(f"\n🔧 Processing {target_file.name}...\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_all_split_tags(content)
    
    if content != original:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed all split tags in {target_file.name}")
    else:
        print(f"ℹ️  No split tags found")
    
    print(f"\n{'=' * 70}")
    print("✅ Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
