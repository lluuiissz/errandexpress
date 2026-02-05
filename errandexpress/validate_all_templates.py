"""
Comprehensive Template Validator
Scans all HTML templates for split tags and syntax issues
"""
import os
import re

template_dir = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates'

def scan_template(file_path):
    """Scan a single template file for issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    # Check for split tags
    for i, line in enumerate(lines, 1):
        if '{%' in line and '%}' not in line:
            issues.append(f"Line {i}: Split template tag")
        if '{{' in line and '}}' not in line:
            issues.append(f"Line {i}: Split variable tag")
    
    # Count if/endif balance
    if_count = sum(1 for line in lines if re.search(r'{%\s*if\s+', line))
    endif_count = sum(1 for line in lines if re.search(r'{%\s*endif\s*%}', line))
    
    return {
        'lines': len(lines),
        'if_count': if_count,
        'endif_count': endif_count,
        'balanced': if_count == endif_count,
        'issues': issues
    }

# Scan all HTML files
print("\n" + "="*70)
print("COMPREHENSIVE TEMPLATE VALIDATION")
print("="*70)

total_files = 0
total_issues = 0
problem_files = []

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, template_dir)
            
            result = scan_template(file_path)
            total_files += 1
            
            if result['issues'] or not result['balanced']:
                total_issues += len(result['issues'])
                if not result['balanced']:
                    total_issues += 1
                problem_files.append((rel_path, result))
                
                print(f"\n⚠️  {rel_path}")
                print(f"   Lines: {result['lines']} | if: {result['if_count']} | endif: {result['endif_count']}")
                if not result['balanced']:
                    print(f"   ❌ UNBALANCED TAGS")
                for issue in result['issues']:
                    print(f"   - {issue}")

print("\n" + "="*70)
print(f"SUMMARY: Scanned {total_files} templates")
if total_issues == 0:
    print(f"✅ NO ISSUES FOUND - All templates are valid!")
else:
    print(f"⚠️  Found {total_issues} issues in {len(problem_files)} files")
print("="*70 + "\n")
