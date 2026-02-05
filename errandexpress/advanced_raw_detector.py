#!/usr/bin/env python3
"""
Advanced Raw Code Detector
Scans for ALL patterns of raw code display
"""

import re
from pathlib import Path

def detect_all_raw_code(content, filename):
    """Detect all possible raw code patterns"""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Pattern 1: {{ word.word|filter without closing }}
        if re.search(r'\{\{\s*\w+\.\w+(?:\|\w+)?(?!\s*\}\})', line):
            if '}}' not in line[line.find('{{'):]:
                issues.append({
                    'line': i,
                    'type': 'Missing closing }}',
                    'content': line.strip()[:80]
                })
        
        # Pattern 2: word.word|filter }} without opening {{
        if re.search(r'(?<!\{\{)\w+\.\w+(?:\|\w+)?\s*\}\}', line):
            before_braces = line[:line.find('}}')]
            if '{{' not in before_braces[-50:]:
                issues.append({
                    'line': i,
                    'type': 'Missing opening {{',
                    'content': line.strip()[:80]
                })
        
        # Pattern 3: Literal template syntax in text
        if re.search(r'\{\{\s*app\.\w+', line) and not re.search(r'\{\{\s*app\.\w+[^}]*\}\}', line):
            issues.append({
                'line': i,
                'type': 'Incomplete variable tag',
                'content': line.strip()[:80]
            })
    
    return issues

def main():
    print("=" * 70)
    print("ADVANCED RAW CODE DETECTOR")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    target_file = templates_dir / 'tasks' / 'applications.html'
    
    print(f"\n🔍 Scanning {target_file.name}...\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = detect_all_raw_code(content, target_file.name)
    
    if issues:
        print(f"⚠️  Found {len(issues)} potential raw code issues:\n")
        for issue in issues:
            print(f"  Line {issue['line']}: {issue['type']}")
            print(f"    {issue['content']}")
            print()
    else:
        print("✅ No raw code issues detected!")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
