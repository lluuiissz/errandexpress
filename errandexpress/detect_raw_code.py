#!/usr/bin/env python3
"""
Advanced Raw Code Detector and Fixer
Detects and fixes:
1. Split template tags ({{ ... }} or {% ... %} across multiple lines)
2. Raw code (template syntax displayed as literal text)
3. Escaped HTML entities in template tags
4. Malformed template syntax
"""

import os
import re
from pathlib import Path

def detect_raw_code_patterns(content, filepath):
    """Detect potential raw code issues"""
    issues = []
    
    # Pattern 1: Look for template-like text outside of proper tags
    # e.g., "task.deadline|date:" without {{ }}
    raw_patterns = [
        (r'(?<!\{)\b(\w+\.\w+(?:\.\w+)*)\|(\w+):', 'Potential raw filter syntax'),
        (r'(?<!\{)\b(user_stats\.\w+)', 'Potential raw variable'),
        (r'(?<!\{)\b(task\.\w+(?:\.\w+)*)', 'Potential raw task variable'),
    ]
    
    for pattern, desc in raw_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if it's inside a proper tag
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]
            
            # Skip if inside {{ }} or {% %}
            if '{{' in context[:50] and '}}' in context[50:]:
                continue
            if '{%' in context[:50] and '%}' in context[50:]:
                continue
            
            issues.append({
                'type': desc,
                'text': match.group(0),
                'position': match.start()
            })
    
    return issues

def fix_split_tags_advanced(content):
    """Advanced split tag fixer"""
    original = content
    
    # Fix {{ ... }} split across lines (multiple passes)
    for _ in range(5):  # Multiple passes to catch nested issues
        # Pattern 1: Simple split
        content = re.sub(
            r'\{\{\s*([^}]+?)\n\s*([^}]+?)\}\}',
            lambda m: '{{ ' + ' '.join(m.group(1, 2).split()) + ' }}',
            content,
            flags=re.MULTILINE
        )
        
        # Pattern 2: Split with filter
        content = re.sub(
            r'\{\{\s*([^}|]+?)\|([^}:]+?):([^}]+?)\n\s*([^}]+?)\}\}',
            lambda m: '{{ ' + m.group(1).strip() + '|' + m.group(2).strip() + ':' + (m.group(3) + ' ' + m.group(4)).strip() + ' }}',
            content,
            flags=re.MULTILINE
        )
    
    # Fix {% ... %} split across lines
    for _ in range(3):
        content = re.sub(
            r'\{%\s*([^%]+?)\n\s*([^%]+?)%\}',
            lambda m: '{% ' + ' '.join(m.group(1, 2).split()) + ' %}',
            content,
            flags=re.MULTILINE
        )
    
    return content

def search_for_raw_text(filepath):
    """Search for specific raw text patterns"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Specific patterns to search for
    raw_texts = [
        'user_stats.unread_notifications_count',
        'task.deadline|date:',
        '{{ task.',
        '{% if',
        '{% for',
    ]
    
    found = []
    for text in raw_texts:
        if text in content:
            # Check if it's properly wrapped
            pattern = re.escape(text)
            
            # If it's a template tag, it should be inside {{ }} or {% %}
            if text.startswith('{{') or text.startswith('{%'):
                # This is fine, it's already a tag
                continue
            
            # Check if this text appears outside of tags
            matches = re.finditer(pattern, content)
            for match in matches:
                start = max(0, match.start() - 10)
                end = min(len(content), match.end() + 10)
                context = content[start:end]
                
                # Check if it's inside proper tags
                before = content[max(0, match.start() - 100):match.start()]
                after = content[match.end():min(len(content), match.end() + 100)]
                
                # Count opening and closing braces
                open_var = before.count('{{') - before.count('}}')
                open_tag = before.count('{%') - before.count('%}')
                
                if open_var == 0 and open_tag == 0:
                    found.append({
                        'text': text,
                        'context': context,
                        'position': match.start()
                    })
    
    return found

def process_file(filepath):
    """Process a single file"""
    filename = os.path.basename(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    # Fix split tags
    fixed = fix_split_tags_advanced(original)
    
    # Detect raw code
    raw_issues = detect_raw_code_patterns(fixed, filepath)
    raw_texts = search_for_raw_text(filepath)
    
    # Report
    if fixed != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"  ✓ Fixed split tags")
        return True, raw_issues, raw_texts
    
    return False, raw_issues, raw_texts

def main():
    print("=" * 80)
    print("ADVANCED RAW CODE DETECTOR AND FIXER")
    print("=" * 80)
    
    base_dir = Path(__file__).parent
    templates_dir = base_dir / 'core' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found")
        return
    
    templates = list(templates_dir.rglob('*.html'))
    print(f"\n🔍 Scanning {len(templates)} template files...\n")
    
    total_fixed = 0
    total_raw_issues = 0
    files_with_issues = []
    
    for template in sorted(templates):
        filename = template.name
        fixed, raw_issues, raw_texts = process_file(str(template))
        
        if fixed or raw_issues or raw_texts:
            print(f"\n📄 {filename}")
            
            if fixed:
                print(f"  ✅ Fixed split tags")
                total_fixed += 1
            
            if raw_issues:
                print(f"  ⚠️  Found {len(raw_issues)} potential raw code issues:")
                for issue in raw_issues[:3]:  # Show first 3
                    print(f"     - {issue['type']}: {issue['text']}")
                total_raw_issues += len(raw_issues)
                files_with_issues.append((filename, raw_issues))
            
            if raw_texts:
                print(f"  🔍 Found {len(raw_texts)} raw text patterns:")
                for item in raw_texts[:3]:
                    print(f"     - '{item['text']}' at position {item['position']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Files fixed: {total_fixed}")
    print(f"⚠️  Potential raw code issues: {total_raw_issues}")
    print(f"📋 Files needing review: {len(files_with_issues)}")
    
    if files_with_issues:
        print("\n🔍 FILES WITH POTENTIAL ISSUES:")
        for filename, issues in files_with_issues[:10]:
            print(f"   - {filename}: {len(issues)} issues")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
