"""
Add missing endif for line 364: {% if user == task.poster %}
"""

file_path = r"c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 364 starts: {% if user == task.poster %}
# Line 442 has: {% else %}
# We need to find where the else block ends and add {% endif %}

# The else block (DOER ACTIONS) should end after line 522 (after the closing </div> for doer actions)
# Let's add the endif after line 522

insert_position = 522  # After line 522 (0-indexed: 521)

# Check what's on line 523
print("Line 523 before:", lines[522].strip())

# Insert endif after line 522
lines.insert(522, '                        {% endif %}\r\n')

print("✅ Added {% endif %} after line 522 to close the {% if user == task.poster %} from line 364")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fix applied!")
