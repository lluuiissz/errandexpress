
import os

def force_fix_applications_html():
    file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\applications.html"
    print(f"Reading {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        skip_next = False
        
        for i in range(len(lines)):
            if skip_next:
                skip_next = False
                continue
                
            line = lines[i]
            stripped = line.strip()
            
            # Check for split {{ ... }}
            # Case 1: line ends with {{
            if stripped.endswith('{{'):
                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i+1]
                    # Merge them
                    # We need to preserve leading whitespace of the first line
                    # and remove leading whitespace of the second line
                    combined = line.rstrip() + ' ' + next_line.lstrip()
                    new_lines.append(combined)
                    skip_next = True
                    print(f"Fixed split '{{' at line {i+1}")
                    continue
            
            # Case 2: line ends with {% else (or similar incomplete tag)
            if '{%' in line and '%}' not in line:
                 if i + 1 < len(lines):
                    next_line = lines[i+1]
                    if '%}' in next_line:
                        combined = line.rstrip() + ' ' + next_line.lstrip()
                        new_lines.append(combined)
                        skip_next = True
                        print(f"Fixed split '{{% ... %}}' at line {i+1}")
                        continue

            # Case 3: Specific Check for the "Match Score" which is very broken
            # <span ... >{{
            # app.calculated_ranking_score|floatformat:1 }}</span>
            
            if '{{' in line and '}}' not in line:
                 if i + 1 < len(lines):
                    next_line = lines[i+1]
                    if '}}' in next_line:
                        combined = line.rstrip() + ' ' + next_line.lstrip()
                        new_lines.append(combined)
                        skip_next = True
                        print(f"Fixed split tag at line {i+1}")
                        continue

            new_lines.append(line)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        print("File rewritten successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_fix_applications_html()
