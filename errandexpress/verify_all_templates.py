import os
import re
from pathlib import Path

def check_template_syntax(file_path):
    """Check a single template file for syntax issues"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Check for split Django tags (tags broken across lines)
    split_tag_pattern = r'{%\s+\w+[^%]*$'  # Tag that doesn't close on same line
    for i, line in enumerate(lines, 1):
        if re.search(split_tag_pattern, line) and not line.strip().endswith('%}'):
            # Check if next line completes it
            if i < len(lines) and '%}' in lines[i]:
                issues.append({
                    'type': 'SPLIT_TAG',
                    'line': i,
                    'content': line.strip(),
                    'severity': 'WARNING'
                })
    
    # 2. Check for imbalanced if/endif tags
    if_count = len(re.findall(r'{%\s*if\s+', content))
    endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
    if if_count != endif_count:
        issues.append({
            'type': 'IMBALANCED_IF',
            'line': 0,
            'content': f'if: {if_count}, endif: {endif_count}',
            'severity': 'ERROR'
        })
    
    # 3. Check for imbalanced for/endfor tags
    for_count = len(re.findall(r'{%\s*for\s+', content))
    endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
    if for_count != endfor_count:
        issues.append({
            'type': 'IMBALANCED_FOR',
            'line': 0,
            'content': f'for: {for_count}, endfor: {endfor_count}',
            'severity': 'ERROR'
        })
    
    # 4. Check for imbalanced block/endblock tags
    block_count = len(re.findall(r'{%\s*block\s+', content))
    endblock_count = len(re.findall(r'{%\s*endblock\s*%}', content))
    if block_count != endblock_count:
        issues.append({
            'type': 'IMBALANCED_BLOCK',
            'line': 0,
            'content': f'block: {block_count}, endblock: {endblock_count}',
            'severity': 'ERROR'
        })
    
    # 5. Check for missing spaces around == in template tags
    no_space_pattern = r'{%\s+if\s+[^%]*==\w'
    for i, line in enumerate(lines, 1):
        if re.search(no_space_pattern, line):
            issues.append({
                'type': 'NO_SPACE_OPERATOR',
                'line': i,
                'content': line.strip(),
                'severity': 'ERROR'
            })
    
    # 6. Check for unclosed template tags
    unclosed_pattern = r'{%[^}]*$'
    for i, line in enumerate(lines, 1):
        if re.search(unclosed_pattern, line) and not line.strip().endswith('%}'):
            issues.append({
                'type': 'UNCLOSED_TAG',
                'line': i,
                'content': line.strip(),
                'severity': 'ERROR'
            })
    
    # 7. Check for unclosed variable tags
    unclosed_var_pattern = r'{{[^}]*$'
    for i, line in enumerate(lines, 1):
        if re.search(unclosed_var_pattern, line) and not line.strip().endswith('}}'):
            issues.append({
                'type': 'UNCLOSED_VARIABLE',
                'line': i,
                'content': line.strip(),
                'severity': 'ERROR'
            })
    
    return issues

def scan_templates(base_dir):
    """Scan all HTML templates in the directory"""
    template_dir = Path(base_dir) / 'core' / 'templates'
    all_issues = {}
    
    for html_file in template_dir.rglob('*.html'):
        issues = check_template_syntax(html_file)
        if issues:
            all_issues[str(html_file)] = issues
    
    return all_issues

def main():
    base_dir = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress"
    
    print("=" * 80)
    print("COMPREHENSIVE TEMPLATE VERIFICATION")
    print("=" * 80)
    
    all_issues = scan_templates(base_dir)
    
    if not all_issues:
        print("\n✅ NO ISSUES FOUND!")
        print("All templates have balanced tags and proper syntax.")
        return
    
    # Print issues by severity
    errors = []
    warnings = []
    
    for file_path, issues in all_issues.items():
        for issue in issues:
            if issue['severity'] == 'ERROR':
                errors.append((file_path, issue))
            else:
                warnings.append((file_path, issue))
    
    # Print errors
    if errors:
        print(f"\n❌ ERRORS FOUND: {len(errors)}")
        print("-" * 80)
        for file_path, issue in errors:
            file_name = Path(file_path).name
            print(f"\n📄 {file_name}")
            print(f"   Type: {issue['type']}")
            if issue['line'] > 0:
                print(f"   Line: {issue['line']}")
            print(f"   Content: {issue['content']}")
    
    # Print warnings
    if warnings:
        print(f"\n⚠️  WARNINGS FOUND: {len(warnings)}")
        print("-" * 80)
        for file_path, issue in warnings:
            file_name = Path(file_path).name
            print(f"\n📄 {file_name}")
            print(f"   Type: {issue['type']}")
            print(f"   Line: {issue['line']}")
            print(f"   Content: {issue['content'][:100]}...")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(errors)} errors, {len(warnings)} warnings")
    print("=" * 80)

if __name__ == "__main__":
    main()
