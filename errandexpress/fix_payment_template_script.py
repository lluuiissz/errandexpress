
import os

file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\payments\task_doer_payment.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The target string to replace (split across lines)
    # matching the indentation exactly as seen in view_file
    old_fragment = """<input type="radio" name="payment_method" value="{{ method.value }}" {% if forloop.first
                                %}checked{% endif %} class="w-4 h-4 text-blue-600">"""
    
    # The replacement string (single line)
    new_fragment = """<input type="radio" name="payment_method" value="{{ method.value }}" {% if forloop.first %}checked{% endif %} class="w-4 h-4 text-blue-600">"""

    if old_fragment in content:
        new_content = content.replace(old_fragment, new_fragment)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("SUCCESS: File updated.")
    else:
        # Fallback: try replacing loosely just in case whitespace differs slightly
        lines = content.splitlines()
        new_lines = []
        skip_next = False
        fixed = False
        for i in range(len(lines)):
            if skip_next:
                skip_next = False
                continue
            
            line = lines[i]
            if '{% if forloop.first' in line and not '%}checked{% endif' in line:
                # Found the start of the split line
                next_line = lines[i+1] if i+1 < len(lines) else ""
                combined = line.rstrip() + " " + next_line.lstrip()
                # Check if it looks like what we want
                if '%}checked{% endif %}' in combined or '%}checked{% endif' in next_line:
                    # Clean up the combined line to match expected single line format
                    # Remove the extra space we added if it was just a newline split
                    # Actually, let's just construct the correct line based on context
                    # The line is: <input ... {% if forloop.first %}checked{% endif %} ...>
                    # We can just replace the whole two lines with the known good line if it matches the pattern
                    if 'input type="radio"' in line:
                         new_lines.append('                            <input type="radio" name="payment_method" value="{{ method.value }}" {% if forloop.first %}checked{% endif %} class="w-4 h-4 text-blue-600">')
                         skip_next = True
                         fixed = True
                         continue
            
            new_lines.append(line)
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print("SUCCESS: File updated (loop method).")
        else:
            print("FAILURE: Target string not found.")
            # Print snippet for debugging
            print("Snippet around line 117:")
            start = max(0, 115)
            for j, l in enumerate(lines[start:125]):
                print(f"{start+j}: {repr(l)}")

except Exception as e:
    print(f"ERROR: {e}")
