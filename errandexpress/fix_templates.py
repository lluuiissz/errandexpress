#!/usr/bin/env python3
"""
Template Fixer Script
Fixes common Django template issues:
1. Split template tags ({{ ... }} or {% ... %} spanning multiple lines)
2. Unbalanced if/endif tags
3. Raw code issues
"""

import os
import re
from pathlib import Path

def fix_split_tags(content):
    """Fix template tags split across multiple lines"""
    # Fix {{ ... }} tags split across lines
    content = re.sub(
        r'\{\{\s*([^}]+?)\n\s*([^}]+?)\}\}',
        lambda m: '{{ ' + ' '.join(m.group(1, 2).split()) + ' }}',
        content,
        flags=re.MULTILINE
    )
    
    # Fix {% ... %} tags split across lines (but not block tags)
    content = re.sub(
        r'\{%\s*(?!if|for|block|endif|endfor|endblock)([^%]+?)\n\s*([^%]+?)%\}',
        lambda m: '{% ' + ' '.join(m.group(1, 2).split()) + ' %}',
        content,
        flags=re.MULTILINE
    )
    
    return content

def count_template_tags(content):
    """Count if/endif, for/endfor, block/endblock tags"""
    tags = {
        'if': len(re.findall(r'\{%\s*if\s+', content)),
        'endif': len(re.findall(r'\{%\s*endif\s*%\}', content)),
        'for': len(re.findall(r'\{%\s*for\s+', content)),
        'endfor': len(re.findall(r'\{%\s*endfor\s*%\}', content)),
        'block': len(re.findall(r'\{%\s*block\s+', content)),
        'endblock': len(re.findall(r'\{%\s*endblock\s*%\}', content)),
    }
    return tags

def fix_task_detail_endif(filepath):
    """Specific fix for task_detail_modern.html missing endif"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find line 543 (0-indexed: 542) and check if it needs endif
    # Insert {% endif %} after line 543 if not present
    insert_line = None
    for i, line in enumerate(lines):
        if i == 543:  # Line 544 (1-indexed)
            # Check if next few lines already have endif
            has_endif = any('{% endif %}' in lines[j] for j in range(i, min(i+5, len(lines))))
            if not has_endif:
                insert_line = i + 1
            break
    
    if insert_line:
        lines.insert(insert_line, '                        {% endif %}\n')
        print(f"✓ Added missing {{% endif %}} at line {insert_line + 1} in {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False

def process_template(filepath):
    """Process a single template file"""
    print(f"\nProcessing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Count tags before
    tags_before = count_template_tags(original_content)
    
    # Fix split tags
    fixed_content = fix_split_tags(original_content)
    
    # Count tags after
    tags_after = count_template_tags(fixed_content)
    
    # Check for imbalances
    issues = []
    if tags_after['if'] != tags_after['endif']:
        issues.append(f"  ⚠ Unbalanced 'if' tags (open={tags_after['if']}, close={tags_after['endif']})")
    if tags_after['for'] != tags_after['endfor']:
        issues.append(f"  ⚠ Unbalanced 'for' tags (open={tags_after['for']}, close={tags_after['endfor']})")
    if tags_after['block'] != tags_after['endblock']:
        issues.append(f"  ⚠ Unbalanced 'block' tags (open={tags_after['block']}, close={tags_after['endblock']})")
    
    # Write if changed
    if fixed_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
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
    """Main execution"""
    print("=" * 60)
    print("Django Template Fixer")
    print("=" * 60)
    
    # Get templates directory
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return
    
    # First, fix the specific task_detail issue
    task_detail_path = templates_dir / 'task_detail_modern.html'
    if task_detail_path.exists():
        print(f"\n🔧 Applying specific fix to task_detail_modern.html...")
        fix_task_detail_endif(str(task_detail_path))
    
    # Find all HTML templates
    templates = list(templates_dir.rglob('*.html'))
    print(f"\nFound {len(templates)} template files")
    
    # Process each template
    all_clean = True
    for template in templates:
        is_clean = process_template(str(template))
        if not is_clean:
            all_clean = False
    
    print("\n" + "=" * 60)
    if all_clean:
        print("✅ All templates processed successfully!")
    else:
        print("⚠ Some templates have unbalanced tags - manual review needed")
    print("=" * 60)

if __name__ == '__main__':
    main()
