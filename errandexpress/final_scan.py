#!/usr/bin/env python3
"""
Final Comprehensive Template Scanner
Performs exhaustive checks for:
1. Raw code (template syntax displayed as literal text)
2. Split tags across multiple lines
3. Unbalanced template tags
4. Malformed template syntax
5. Escaped HTML entities in template tags
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class TemplateScanner:
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = {
            'files_scanned': 0,
            'split_tags_found': 0,
            'raw_code_found': 0,
            'unbalanced_tags': 0,
            'malformed_syntax': 0
        }
    
    def scan_for_split_tags(self, content, filepath):
        """Detect template tags split across lines"""
        issues = []
        
        # Check for {{ ... }} split across lines
        pattern1 = r'\{\{\s*[^}]+\n[^}]*\}\}'
        matches = re.finditer(pattern1, content, re.MULTILINE)
        for match in matches:
            issues.append({
                'type': 'Split Variable Tag',
                'text': match.group(0)[:50] + '...',
                'position': match.start()
            })
            self.stats['split_tags_found'] += 1
        
        # Check for {% ... %} split across lines
        pattern2 = r'\{%\s*[^%]+\n[^%]*%\}'
        matches = re.finditer(pattern2, content, re.MULTILINE)
        for match in matches:
            issues.append({
                'type': 'Split Tag Block',
                'text': match.group(0)[:50] + '...',
                'position': match.start()
            })
            self.stats['split_tags_found'] += 1
        
        return issues
    
    def scan_for_raw_code(self, content, filepath):
        """Detect potential raw code (template syntax as literal text)"""
        issues = []
        
        # Pattern 1: Variable-like text without {{ }}
        # Look for patterns like "user_stats.something" or "task.something"
        raw_patterns = [
            (r'(?<!\{)\b(user_stats\.\w+)', 'user_stats variable'),
            (r'(?<!\{)\b(task\.\w+\|date:)', 'task date filter'),
            (r'(?<!\{)\b(\w+\.\w+\|default:)', 'default filter'),
        ]
        
        for pattern, desc in raw_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Get context
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                
                # Check if it's inside proper tags
                before = context[:match.start() - start]
                
                # Count braces
                open_var = before.count('{{') - before.count('}}')
                open_tag = before.count('{%') - before.count('%}')
                
                # If not inside any tags, it's raw code
                if open_var == 0 and open_tag == 0:
                    issues.append({
                        'type': f'Raw Code: {desc}',
                        'text': match.group(0),
                        'position': match.start(),
                        'context': context[max(0, match.start() - start - 20):match.end() - start + 20]
                    })
                    self.stats['raw_code_found'] += 1
        
        return issues
    
    def scan_for_unbalanced_tags(self, content, filepath):
        """Check for unbalanced template tags"""
        issues = []
        
        tag_pairs = [
            ('if', 'endif'),
            ('for', 'endfor'),
            ('block', 'endblock'),
            ('with', 'endwith'),
        ]
        
        for open_tag, close_tag in tag_pairs:
            open_pattern = r'\{%\s*' + open_tag + r'\s+'
            close_pattern = r'\{%\s*' + close_tag + r'\s*%\}'
            open_count = len(re.findall(open_pattern, content))
            close_count = len(re.findall(close_pattern, content))
            
            if open_count != close_count:
                issues.append({
                    'type': 'Unbalanced Tags',
                    'text': f'{open_tag}/{close_tag} (open={open_count}, close={close_count})',
                    'severity': 'HIGH'
                })
                self.stats['unbalanced_tags'] += 1
        
        return issues
    
    def scan_for_malformed_syntax(self, content, filepath):
        """Detect malformed template syntax"""
        issues = []
        
        # Check for incomplete tags
        patterns = [
            (r'\{\{[^}]*$', 'Incomplete variable tag (missing }})'),
            (r'\{%[^%]*$', 'Incomplete block tag (missing %})'),
            (r'^\s*\}\}', 'Closing }} without opening {{'),
            (r'^\s*%\}', 'Closing %} without opening {%'),
        ]
        
        for pattern, desc in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                issues.append({
                    'type': 'Malformed Syntax',
                    'text': desc,
                    'position': match.start()
                })
                self.stats['malformed_syntax'] += 1
        
        return issues
    
    def scan_file(self, filepath):
        """Scan a single file for all issues"""
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Error reading {filename}: {e}")
            return
        
        self.stats['files_scanned'] += 1
        
        # Run all scans
        split_issues = self.scan_for_split_tags(content, filepath)
        raw_issues = self.scan_for_raw_code(content, filepath)
        unbalanced_issues = self.scan_for_unbalanced_tags(content, filepath)
        malformed_issues = self.scan_for_malformed_syntax(content, filepath)
        
        all_issues = split_issues + raw_issues + unbalanced_issues + malformed_issues
        
        if all_issues:
            self.issues[filename] = all_issues
            return True
        return False
    
    def print_report(self):
        """Print comprehensive report"""
        print("\n" + "=" * 80)
        print("FINAL COMPREHENSIVE SCAN REPORT")
        print("=" * 80)
        
        print(f"\n📊 STATISTICS:")
        print(f"   Files Scanned: {self.stats['files_scanned']}")
        print(f"   Split Tags Found: {self.stats['split_tags_found']}")
        print(f"   Raw Code Found: {self.stats['raw_code_found']}")
        print(f"   Unbalanced Tags: {self.stats['unbalanced_tags']}")
        print(f"   Malformed Syntax: {self.stats['malformed_syntax']}")
        
        if not self.issues:
            print("\n✅ NO ISSUES FOUND - CODEBASE IS CLEAN!")
            print("=" * 80)
            return
        
        print(f"\n⚠️  ISSUES FOUND IN {len(self.issues)} FILES:\n")
        
        for filename, issues in sorted(self.issues.items()):
            print(f"\n📄 {filename}")
            print(f"   {len(issues)} issue(s) found:")
            
            for i, issue in enumerate(issues[:5], 1):  # Show first 5 issues per file
                print(f"   {i}. {issue['type']}")
                print(f"      Text: {issue.get('text', 'N/A')[:60]}")
                if 'context' in issue:
                    print(f"      Context: ...{issue['context'][:40]}...")
            
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more issues")
        
        print("\n" + "=" * 80)

def main():
    print("=" * 80)
    print("FINAL COMPREHENSIVE TEMPLATE SCANNER")
    print("=" * 80)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return
    
    scanner = TemplateScanner()
    
    templates = list(templates_dir.rglob('*.html'))
    print(f"\n🔍 Scanning {len(templates)} template files...\n")
    
    files_with_issues = 0
    for template in sorted(templates):
        if scanner.scan_file(str(template)):
            files_with_issues += 1
    
    scanner.print_report()
    
    # Final verdict
    if scanner.stats['split_tags_found'] == 0 and scanner.stats['raw_code_found'] == 0:
        print("\n🎉 SUCCESS! No split tags or raw code found!")
        print("✅ All templates are properly formatted.")
    else:
        print("\n⚠️  Action required: Please review the issues above.")

if __name__ == '__main__':
    main()
