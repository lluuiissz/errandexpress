#!/usr/bin/env python3
"""
Comprehensive Django Template Tag Fixer
Scans all HTML templates and fixes broken/split Django template tags
"""
import os
import re
from pathlib import Path

def fix_split_django_tags(file_path):
    """Fix split Django template tags in a file"""
    print(f"\n{'='*80}")
    print(f"Scanning: {file_path}")
    print('='*80)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Pattern 1: Split variable tags {{ ... }}
        # Matches: {{ \n content \n }}
        pattern1 = r'(\{\{)\s*\n\s*(.*?)\s*(\}\})'
        matches1 = list(re.finditer(pattern1, content, re.DOTALL))
        
        for match in matches1:
            full_match = match.group(0)
            inner = match.group(2).strip()
            
            # Only fix if it's a simple split (not multi-line logic)
            if '\n' in inner and len(inner.split('\n')) <= 3:
                fixed = f"{{{{ {inner} }}}}"
                content = content.replace(full_match, fixed, 1)
                fixes_made += 1
                print(f"  ✓ Fixed split variable tag: {{ {inner[:50]}... }}")
        
        # Pattern 2: Split block tags {% ... %}
        # Matches: {% \n content \n %}
        pattern2 = r'(\{%)\s*\n\s*(.*?)\s*(%\})'
        matches2 = list(re.finditer(pattern2, content, re.DOTALL))
        
        for match in matches2:
            full_match = match.group(0)
            inner = match.group(2).strip()
            
            # Only fix if it's a simple split (not multi-line logic)
            if '\n' in inner and len(inner.split('\n')) <= 3:
                fixed = f"{{% {inner} %}}"
                content = content.replace(full_match, fixed, 1)
                fixes_made += 1
                print(f"  ✓ Fixed split block tag: {{% {inner[:50]}... %}}")
        
        # Pattern 3: Broken tags like "Spent{%" followed by "endif %}"
        # This is the most dangerous pattern
        pattern3 = r'(\{%)\s*\n\s*(endif|endfor|endblock|endwith|endcomment)\s*(%\})'
        matches3 = list(re.finditer(pattern3, content, re.DOTALL))
        
        for match in matches3:
            full_match = match.group(0)
            tag_name = match.group(2)
            fixed = f"{{% {tag_name} %}}"
            content = content.replace(full_match, fixed, 1)
            fixes_made += 1
            print(f"  ✓ Fixed broken end tag: {{% {tag_name} %}}")
        
        # Pattern 4: Tags split mid-word like "Spent{%\n                                endif %}"
        # Look for text followed by {% on same line, then tag name on next line
        pattern4 = r'(\w+)(\{%)\s*\n\s*(\w+)\s+(%\})'
        matches4 = list(re.finditer(pattern4, content))
        
        for match in matches4:
            full_match = match.group(0)
            text_before = match.group(1)
            tag_name = match.group(3)
            
            # This is likely "Spent{% \n endif %}" pattern
            if tag_name in ['endif', 'endfor', 'endblock', 'endwith', 'else', 'elif']:
                fixed = f"{text_before}{{% {tag_name} %}}"
                content = content.replace(full_match, fixed, 1)
                fixes_made += 1
                print(f"  ✓ Fixed mid-word split: {text_before}{{% {tag_name} %}}")
        
        # Save if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✅ Fixed {fixes_made} issues in {file_path}")
            return fixes_made
        else:
            print(f"  ℹ️  No issues found")
            return 0
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0

def scan_templates(base_dir):
    """Scan all template files in the project"""
    templates_dir = Path(base_dir) / 'errandexpress' / 'core' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return
    
    print(f"\n🔍 Scanning templates in: {templates_dir}")
    print(f"{'='*80}\n")
    
    total_files = 0
    total_fixes = 0
    
    # Find all HTML files
    for html_file in templates_dir.rglob('*.html'):
        total_files += 1
        fixes = fix_split_django_tags(html_file)
        total_fixes += fixes
    
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"Files scanned: {total_files}")
    print(f"Total fixes applied: {total_fixes}")
    print(f"{'='*80}\n")
    
    if total_fixes > 0:
        print("✅ Template tags have been fixed!")
        print("🔄 Please refresh your browser to see the changes.")
    else:
        print("ℹ️  No broken template tags found.")

if __name__ == "__main__":
    base_dir = os.getcwd()
    print(f"Working directory: {base_dir}")
    scan_templates(base_dir)
