"""
Comprehensive Codebase Analysis Script
Checks for split tags, broken lines, raw code, and other issues
"""

import os
import re
from pathlib import Path

print("=" * 80)
print("COMPREHENSIVE CODEBASE ANALYSIS")
print("=" * 80)

# Configuration
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'core' / 'templates'
PYTHON_FILES = [
    'core/views.py',
    'core/models.py',
    'core/forms.py',
    'core/services.py',
    'core/api_views.py',
]

issues_found = []

# Test 1: Check for split Django template tags
print("\n✓ Test 1: Checking for split template tags...")
if TEMPLATE_DIR.exists():
    html_files = list(TEMPLATE_DIR.rglob('*.html'))
    print(f"  Found {len(html_files)} HTML templates")
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Check for unclosed variable tags
                    if '{{' in line and '}}' not in line:
                        issues_found.append({
                            'file': html_file.name,
                            'line': i,
                            'type': 'Split variable tag',
                            'content': line.strip()[:50]
                        })
                    
                    # Check for unclosed template tags
                    if '{%' in line and '%}' not in line:
                        issues_found.append({
                            'file': html_file.name,
                            'line': i,
                            'type': 'Split template tag',
                            'content': line.strip()[:50]
                        })
        except Exception as e:
            print(f"  ⚠️  Error reading {html_file.name}: {e}")

if not issues_found:
    print("  ✅ No split tags found")
else:
    print(f"  ⚠️  Found {len(issues_found)} potential split tags")

# Test 2: Check for raw/debug code
print("\n✓ Test 2: Checking for raw/debug code...")
debug_patterns = [
    r'console\.log\(',
    r'print\(["\']DEBUG',
    r'import pdb',
    r'breakpoint\(\)',
    r'debugger;',
    r'TODO:',
    r'FIXME:',
    r'XXX:',
]

debug_issues = []
for py_file in PYTHON_FILES:
    file_path = BASE_DIR / py_file
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for pattern in debug_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            debug_issues.append({
                                'file': py_file,
                                'line': i,
                                'type': 'Debug code',
                                'pattern': pattern,
                                'content': line.strip()[:60]
                            })
        except Exception as e:
            print(f"  ⚠️  Error reading {py_file}: {e}")

if not debug_issues:
    print("  ✅ No debug code found")
else:
    print(f"  ⚠️  Found {len(debug_issues)} debug statements")
    for issue in debug_issues[:5]:  # Show first 5
        print(f"    - {issue['file']}:{issue['line']} - {issue['pattern']}")

# Test 3: Check for broken lines (very long lines)
print("\n✓ Test 3: Checking for excessively long lines...")
long_lines = []
for py_file in PYTHON_FILES:
    file_path = BASE_DIR / py_file
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if len(line) > 200:  # PEP 8 recommends 79, we're lenient at 200
                        long_lines.append({
                            'file': py_file,
                            'line': i,
                            'length': len(line),
                            'content': line.strip()[:60] + '...'
                        })
        except Exception as e:
            print(f"  ⚠️  Error reading {py_file}: {e}")

if not long_lines:
    print("  ✅ No excessively long lines found")
else:
    print(f"  ⚠️  Found {len(long_lines)} lines over 200 characters")

# Test 4: Check for common syntax issues
print("\n✓ Test 4: Checking Python syntax...")
syntax_errors = []
for py_file in PYTHON_FILES:
    file_path = BASE_DIR / py_file
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, str(file_path), 'exec')
            print(f"  ✅ {py_file} - Syntax OK")
        except SyntaxError as e:
            syntax_errors.append({
                'file': py_file,
                'line': e.lineno,
                'error': str(e)
            })
            print(f"  ❌ {py_file} - Syntax Error at line {e.lineno}")

# Summary
print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)
print(f"Split tags: {len(issues_found)}")
print(f"Debug code: {len(debug_issues)}")
print(f"Long lines: {len(long_lines)}")
print(f"Syntax errors: {len(syntax_errors)}")

total_issues = len(issues_found) + len(debug_issues) + len(syntax_errors)
if total_issues == 0:
    print("\n✅ CODEBASE IS CLEAN!")
else:
    print(f"\n⚠️  Total issues found: {total_issues}")
    
    # Show detailed issues
    if issues_found:
        print("\nSplit Tag Issues:")
        for issue in issues_found[:10]:
            print(f"  - {issue['file']}:{issue['line']} - {issue['type']}")
    
    if syntax_errors:
        print("\nSyntax Errors:")
        for error in syntax_errors:
            print(f"  - {error['file']}:{error['line']} - {error['error']}")

print("\n" + "=" * 80)
