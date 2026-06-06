
import os
import re
import sys

def fix_split_tags(directory):
    print(f"Scanning directory: {directory} for split tags...")
    
    # Regex to find tags that might contain newlines
    # matches {% ... %} - conservative match to avoid matching across multiple tags if malformed
    block_tag_pattern = re.compile(r'({%[^{}%]*?%})', re.DOTALL)
    # matches {{ ... }}
    var_tag_pattern = re.compile(r'({{[^{}]*?}})', re.DOTALL)

    files_fixed = 0
    total_tags_fixed = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.html'):
                continue
            
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                print(f"Skipping binary/encoding error file: {path}")
                continue
            
            original_content = content
            file_tags_fixed = 0
            
            def replace_callback(match):
                tag = match.group(0)
                if '\n' in tag:
                    # Normalize whitespace: replace newlines and multiple spaces with single space
                    normalized = re.sub(r'\s+', ' ', tag)
                    # print(f"  Found split tag in {file}: {tag[:20]}... -> {normalized[:20]}...")
                    nonlocal file_tags_fixed
                    file_tags_fixed += 1
                    return normalized
                return tag
            
            # Apply fixes
            new_content = block_tag_pattern.sub(replace_callback, content)
            new_content = var_tag_pattern.sub(replace_callback, new_content)
            
            if new_content != original_content:
                print(f"Checked {file}: Found {file_tags_fixed} split tags. Fixing...")
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    files_fixed += 1
                    total_tags_fixed += file_tags_fixed
                except Exception as e:
                    print(f"Error writing file {path}: {e}")

    print(f"\n--- SUMMARY ---")
    print(f"Files modified: {files_fixed}")
    print(f"Total split tags merged: {total_tags_fixed}")
    print(f"Scan complete.")

if __name__ == '__main__':
    target_dir = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates'
    if not os.path.exists(target_dir):
        print(f"Error: Directory not found: {target_dir}")
    else:
        fix_split_tags(target_dir)
