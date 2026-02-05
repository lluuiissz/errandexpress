
import re
import os

def fix_split_tags(file_path):
    print(f"Propcessing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Regex to find split {{ ... }} tags
        # Logic: Find '{{' at the end of a line (ignoring whitespace), followed by next line content
        # We'll use a loop to handle multiple occurrences
        
        lines = content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for split {{ tag
            # If line ends with {{ or contains {{ but doesn't have }} and next line completes it
            
            stripped_line = line.strip()
            
            # Simple heuristic: if line ends with {{ or {%
            if stripped_line.endswith('{{') or stripped_line.endswith('{%'):
                # Check if next line exists
                if i + 1 < len(lines):
                    next_line = lines[i+1]
                    print(f"Found split tag at line {i+1}:")
                    print(f"  Line A: {line}")
                    print(f"  Line B: {next_line}")
                    
                    # Merge logic: preserve leading whitespace of first line, 
                    # strip leading whitespace of second line
                    merged_line = line.rstrip() + ' ' + next_line.lstrip()
                    print(f"  Merged: {merged_line}")
                    new_lines.append(merged_line)
                    i += 2 # Skip next line since we merged it
                    continue
            
            # Check for split where {{ is on one line and variable is on next
            # Regex for literal '{{' followed by only whitespace at end of line
            if re.search(r'\{\{\s*$', line):
                 if i + 1 < len(lines):
                    next_line = lines[i+1]
                    print(f"Found split code block at line {i+1}:")
                    merged_line = line.rstrip() + ' ' + next_line.lstrip()
                    new_lines.append(merged_line)
                    i += 2
                    continue

            new_lines.append(line)
            i += 1
            
        # Reconstruct content
        new_content = '\n'.join(new_lines)
        
        if new_content != original_content:
            print("Changes detected. Saving file...")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("File saved successfully.")
        else:
            print("No split tags detected.")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    target_file = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\admin_dashboard_modern.html"
    if os.path.exists(target_file):
        fix_split_tags(target_file)
    else:
        print(f"File not found: {target_file}")
