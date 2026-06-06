#!/usr/bin/env python3
"""
URL Tag Validator
Checks for common URL tag errors in Django templates
"""

import os
import re
from pathlib import Path

def check_url_tags(content, filepath):
    """Check for malformed URL tags"""
    issues = []
    
    # Pattern 1: Space after {% url
    pattern1 = r"\{%\s*url\s+'\s+(\w+)"
    matches = re.finditer(pattern1, content)
    for match in matches:
        issues.append({
            'type': 'Space in URL name',
            'text': f"' {match.group(1)}'",
            'fix': f"'{match.group(1)}'"
        })
    
    # Pattern 2: Space before closing quote
    pattern2 = r"\{%\s*url\s+'(\w+)\s+'"
    matches = re.finditer(pattern2, content)
    for match in matches:
        issues.append({
            'type': 'Space before closing quote',
            'text': f"'{match.group(1)} '",
            'fix': f"'{match.group(1)}'"
        })
    
    return issues

def main():
    print("=" * 70)
    print("URL TAG VALIDATOR")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    templates = list(templates_dir.rglob('*.html'))
    print(f"\n🔍 Checking {len(templates)} templates for URL tag errors...\n")
    
    total_issues = 0
    for template in sorted(templates):
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = check_url_tags(content, str(template))
        if issues:
            print(f"\n📄 {template.name}")
            for issue in issues:
                print(f"  ⚠️  {issue['type']}: {issue['text']}")
                print(f"     Should be: {issue['fix']}")
                total_issues += 1
    
    print(f"\n{'=' * 70}")
    if total_issues == 0:
        print("✅ No URL tag errors found!")
    else:
        print(f"⚠️  Found {total_issues} URL tag issues")
    print("=" * 70)

if __name__ == '__main__':
    main()
