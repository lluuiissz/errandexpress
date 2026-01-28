"""
Comprehensive script to fix ALL split Django template tags across the entire codebase.
This script will:
1. Find all HTML template files
2. Detect and join split {% ... %} and {{ ... }} tags
3. Fix them in place
4. Report all changes made
"""

import os
import re
from pathlib import Path

def fix_split_tags_in_file(filepath):
    """Fix split template tags in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Pattern 1: Fix split {% ... %} tags (Django template tags)
        # Matches {% ... that continues on next line with ... %}
        pattern1 = r'\{%\s+([^%}]*?)\r?\n\s*([^%}]*?)\s*%\}'
        
        def replace_template_tag(match):
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            joined = f'{{% {part1} {part2} %}}'
            changes_made.append(f"Joined template tag: {match.group(0)[:50]}... -> {joined}")
            return joined
        
        content = re.sub(pattern1, replace_template_tag, content)
        
        # Pattern 2: Fix split {{ ... }} tags (Django variable tags)
        # Matches {{ ... that continues on next line with ... }}
        pattern2 = r'\{\{\s+([^}]*?)\r?\n\s*([^}]*?)\s*\}\}'
        
        def replace_variable_tag(match):
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            joined = f'{{{{ {part1} {part2} }}}}'
            changes_made.append(f"Joined variable tag: {match.group(0)[:50]}... -> {joined}")
            return joined
        
        content = re.sub(pattern2, replace_variable_tag, content)
        
        # Pattern 3: Fix more complex multi-line splits
        # This handles cases where the tag is split across multiple lines
        pattern3 = r'\{%\s+([^%}]*?)(?:\r?\n\s*)+([^%}]*?)\s*%\}'
        content = re.sub(pattern3, lambda m: f'{{% {m.group(1).strip()} {m.group(2).strip()} %}}', content)
        
        pattern4 = r'\{\{\s+([^}]*?)(?:\r?\n\s*)+([^}]*?)\s*\}\}'
        content = re.sub(pattern4, lambda m: f'{{{{ {m.group(1).strip()} {m.group(2).strip()} }}}}', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        
        return False, []
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False, []

def scan_and_fix_templates(root_dir):
    """Scan all template files and fix split tags."""
    root_path = Path(root_dir)
    template_files = []
    
    # Find all .html files
    for html_file in root_path.rglob('*.html'):
        template_files.append(html_file)
    
    print(f"Found {len(template_files)} HTML template files")
    print("=" * 80)
    
    total_fixed = 0
    files_modified = []
    
    for template_file in template_files:
        was_fixed, changes = fix_split_tags_in_file(template_file)
        
        if was_fixed:
            total_fixed += 1
            files_modified.append(str(template_file))
            print(f"\nFIXED: {template_file}")
            for change in changes:
                print(f"   - {change}")
    
    print("\n" + "=" * 80)
    print(f"\nSUMMARY:")
    print(f"   Total files scanned: {len(template_files)}")
    print(f"   Files modified: {total_fixed}")
    
    if files_modified:
        print(f"\nModified files:")
        for filepath in files_modified:
            print(f"   - {filepath}")
    else:
        print("\nNo split tags found! All templates are clean.")
    
    return total_fixed

if __name__ == "__main__":
    # Start from the errandexpress directory
    project_root = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress"
    
    print("Scanning for split Django template tags...")
    print(f"Root directory: {project_root}\n")
    
    fixed_count = scan_and_fix_templates(project_root)
    
    print(f"\nComplete! Fixed {fixed_count} file(s).")
