import re

# Read the file
file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove line 520 (index 519) which has the extra endif tag
# Line 519 (index 518): {% endif %} - keep (closes line 513)
# Line 520 (index 519): {% endif %} - REMOVE (extra)
# Line 521 (index 520): </div> - keep

if len(lines) > 519:
    # Check if line 520 contains endif
    line_520 = lines[519].strip()
    if 'endif' in line_520:
        print("Line 520 before:", line_520)
        # Remove line 520
        del lines[519]
        print("✅ Removed extra endif tag at line 520")
    else:
        print("⚠️ Line 520 doesn't contain endif:", line_520)
else:
    print("⚠️ File has fewer than 520 lines")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Template fixed!")
