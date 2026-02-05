"""
Add missing endif tag for the Preferences & Scheduling section
"""

file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The Preferences section starts at line 161 with an if
# It should close after line 287 (after the closing </div>)
# Line 288 currently has an endif, but we need to verify it's in the right place

# Let's check if line 288 is the endif for line 161
# If not, we need to add one after line 287

# Insert endif after line 287 (before current line 288)
if len(lines) > 287:
    # Check if line 288 already has endif
    if '{% endif %}' in lines[287]:
        print("Line 288 already has endif")
        print("Content:", lines[287].strip())
    else:
        # Add endif after line 287
        lines.insert(287, '                {% endif %}\r\n')
        print("✅ Added missing endif after line 287")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fix applied!")
