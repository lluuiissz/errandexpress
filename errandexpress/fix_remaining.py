#!/usr/bin/env python3
"""
Fix Remaining Template Issues
Targeting applications.html and task_detail_modern.html
"""

import re
from pathlib import Path

def fix_applications(content):
    # Fix split elif tags
    # Pattern: {% elif \n task.status... %}
    content = re.sub(
        r'\{%\s*elif\s*\n\s*([^%]+?)\s*%\}',
        lambda m: f"{{% elif {m.group(1).strip()} %}}",
        content,
        flags=re.MULTILINE
    )
    return content

def fix_task_detail(content):
    # Fix raw code display for date filter
    # Look for {{ task.accepted_at|date: without arguments or closing }}
    # It might be {{ task.accepted_at|date:"M d, Y" }} but split
    
    # Fix split tags generally first
    content = re.sub(
        r'\{\{\s*([^}]+?)\n\s*([^}]+?)\}\}',
        lambda m: '{{ ' + ' '.join(m.group(1, 2).split()) + ' }}',
        content,
        flags=re.MULTILINE
    )
    return content

def main():
    print("=" * 70)
    print("FIXING REMAINING ISSUES")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    
    # 1. Fix applications.html
    app_file = base_dir / 'core' / 'templates' / 'tasks' / 'applications.html'
    if app_file.exists():
        print(f"Processing {app_file.name}...")
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = fix_applications(content)
        if new_content != content:
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Fixed split {% elif %} in applications.html")
        else:
            print("ℹ️  No changes needed for applications.html")

    # 2. Fix task_detail_modern.html
    detail_file = base_dir / 'core' / 'templates' / 'task_detail_modern.html'
    if detail_file.exists():
        print(f"Processing {detail_file.name}...")
        with open(detail_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = fix_task_detail(content)
        if new_content != content:
            with open(detail_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Fixed split tags in task_detail_modern.html")
        else:
            print("ℹ️  No changes needed for task_detail_modern.html")
            
    print(f"\n{'=' * 70}")
    print("✅ Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
