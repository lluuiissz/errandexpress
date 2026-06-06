#!/usr/bin/env python3
"""
Comprehensive Template Fixer
Fixes all Django template issues including split tags and unbalanced blocks
"""

import os
import re
from pathlib import Path

def fix_split_variable_tags(content):
    """Fix {{ ... }} tags split across multiple lines"""
    # Pattern to match {{ ... }} spanning multiple lines
    pattern = r'\{\{\s*([^\}]+?)\n\s*([^\}]+?)\}\}'
    
    def replacer(match):
        # Combine the two groups and normalize whitespace
        combined = match.group(1).strip() + ' ' + match.group(2).strip()
        return '{{ ' + combined + ' }}'
    
    # Keep applying until no more matches
    prev_content = None
    while prev_content != content:
        prev_content = content
        content = re.sub(pattern, replacer, content, flags=re.MULTILINE)
    
    return content

def fix_my_tasks_specific(filepath):
    """Specific fix for my_tasks_modern.html split date tag"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific split tag issue
    original = content
    
    # Pattern 1: Fix date filter split across lines
    content = re.sub(
        r'\{\{\s*task\.deadline\|date:"M\s*\n\s*d,\s*Y"\s*\}\}',
        '{{ task.deadline|date:"M d, Y" }}',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 2: More general fix for any filter split
    content = re.sub(
        r'\{\{\s*([^}]+?)\|([^:}]+?):"([^"]+?)"\s*\n\s*([^"]+?)"\s*\}\}',
        lambda m: '{{ ' + m.group(1) + '|' + m.group(2) + ':"' + m.group(3) + ' ' + m.group(4) + '" }}',
        content,
        flags=re.MULTILINE
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_task_detail_endif(filepath):
    """Fix missing endif in task_detail_modern.html"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Count if/endif to find imbalance
    if_count = sum(1 for line in lines if re.search(r'\{%\s*if\s+', line))
    endif_count = sum(1 for line in lines if re.search(r'\{%\s*endif\s*%\}', line))
    
    if if_count > endif_count:
        # Find line 543 (where the doer actions end)
        for i in range(len(lines)):
            if i == 543:  # Line 544 in 1-indexed
                # Check if endif already exists nearby
                has_endif = any('{% endif %}' in lines[j] for j in range(max(0, i-2), min(i+5, len(lines))))
                if not has_endif:
                    # Insert endif before the closing div
                    lines.insert(i, '                        {% endif %}\n')
                    print(f"  ✓ Added missing endif at line {i+1}")
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True
                break
    return False

def count_tags(content):
    """Count template tags"""
    return {
        'if': len(re.findall(r'\{%\s*if\s+', content)),
        'endif': len(re.findall(r'\{%\s*endif\s*%\}', content)),
        'for': len(re.findall(r'\{%\s*for\s+', content)),
        'endfor': len(re.findall(r'\{%\s*endfor\s*%\}', content)),
    }

def process_template(filepath):
    """Process a single template"""
    filename = os.path.basename(filepath)
    print(f"\nProcessing: {filename}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    # Apply fixes
    fixed = fix_split_variable_tags(original)
    
    # Count tags
    tags = count_tags(fixed)
    
    # Check balance
    issues = []
    if tags['if'] != tags['endif']:
        issues.append(f"  ⚠ Unbalanced if/endif (if={tags['if']}, endif={tags['endif']})")
    if tags['for'] != tags['endfor']:
        issues.append(f"  ⚠ Unbalanced for/endfor (for={tags['for']}, endfor={tags['endfor']})")
    
    # Write if changed
    if fixed != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"  ✓ Fixed split tags")
    else:
        print(f"  ✓ No split tags found")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print(f"  ✓ All tags balanced")
    
    return len(issues) == 0

def main():
    print("=" * 70)
    print("COMPREHENSIVE DJANGO TEMPLATE FIXER")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return
    
    # Priority fixes first
    print("\n🔧 APPLYING PRIORITY FIXES...")
    print("-" * 70)
    
    # Fix my_tasks_modern.html
    my_tasks = templates_dir / 'tasks' / 'my_tasks_modern.html'
    if my_tasks.exists():
        print(f"\n📝 Fixing my_tasks_modern.html...")
        if fix_my_tasks_specific(str(my_tasks)):
            print("  ✓ Fixed split date tag")
        else:
            print("  ℹ No changes needed")
    
    # Fix task_detail_modern.html
    task_detail = templates_dir / 'task_detail_modern.html'
    if task_detail.exists():
        print(f"\n📝 Fixing task_detail_modern.html...")
        if fix_task_detail_endif(str(task_detail)):
            print("  ✓ Fixed missing endif")
        else:
            print("  ℹ No changes needed")
    
    # Process all templates
    print("\n\n🔍 SCANNING ALL TEMPLATES...")
    print("-" * 70)
    
    templates = list(templates_dir.rglob('*.html'))
    print(f"Found {len(templates)} template files\n")
    
    all_clean = True
    for template in sorted(templates):
        is_clean = process_template(str(template))
        if not is_clean:
            all_clean = False
    
    print("\n" + "=" * 70)
    if all_clean:
        print("✅ ALL TEMPLATES PROCESSED SUCCESSFULLY!")
    else:
        print("⚠ SOME TEMPLATES HAVE UNBALANCED TAGS")
        print("   (These may need manual review)")
    print("=" * 70)

if __name__ == '__main__':
    main()
