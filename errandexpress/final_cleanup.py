#!/usr/bin/env python3
"""
Final Template Cleanup Script
Fixes all remaining template issues with careful pattern matching
"""

import re
from pathlib import Path

def fix_duplicate_braces(content):
    """Remove duplicate {{ or }} in template tags"""
    # Fix {{ {{ pattern
    content = re.sub(r'\{\{\s*\{\{', '{{', content)
    # Fix }} }} pattern
    content = re.sub(r'\}\}\s*\}\}', '}}', content)
    return content

def main():
    print("=" * 70)
    print("FINAL TEMPLATE CLEANUP")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    target_file = base_dir / 'core' / 'templates' / 'tasks' / 'applications.html'
    
    print(f"\n🔧 Cleaning {target_file.name}...\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_duplicate_braces(content)
    
    if content != original:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed duplicate braces in {target_file.name}")
    else:
        print(f"ℹ️  No duplicate braces found")
    
    print(f"\n{'=' * 70}")
    print("✅ Cleanup complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
