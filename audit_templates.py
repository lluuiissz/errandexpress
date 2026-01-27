import os
import re

def scan_templates(root_dir):
    print(f"Scanning templates in {root_dir}...")
    error_count = 0
    
    # Regex for split tags: {% ... (newline) ... %}
    # This detects tags that start but don't close on the same line
    split_tag_pattern = re.compile(r'({%[^%\}]*\n[^%]*%})')
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for split tags
                    matches = split_tag_pattern.findall(content)
                    if matches:
                        print(f"\n[ERROR] Split tags found in: {file_path}")
                        for match in matches:
                            # Show the first few chars of the match
                            snippet = match.replace('\n', '\\n')[:100]
                            print(f"  - Found: {snippet}...")
                        error_count += 1
                        
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    if error_count == 0:
        print("\n✅ No split tags found.")
    else:
        print(f"\n❌ Found errors in {error_count} files.")

if __name__ == "__main__":
    scan_templates("c:\\Users\\Admin\\Desktop\\errandexpress - Copy\\errandexpress\\core\\templates")
