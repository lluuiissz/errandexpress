# Script to add is_new property to Task model
import os

file_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\models.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line after get_tags_list method
insert_index = None
for i, line in enumerate(lines):
    if 'def get_tags_list(self):' in line:
        # Find the end of this method (next blank line or class Meta)
        for j in range(i+1, len(lines)):
            if lines[j].strip() == '' or 'class Meta:' in lines[j]:
                insert_index = j
                break
        break

if insert_index:
    # Insert the new property
    new_lines = [
        '\n',
        '    @property\n',
        '    def is_new(self):\n',
        '        """Check if task was posted within the last 24 hours"""\n',
        '        from django.utils import timezone\n',
        '        from datetime import timedelta\n',
        '        return timezone.now() - self.created_at < timedelta(hours=24)\n',
    ]
    
    for idx, new_line in enumerate(new_lines):
        lines.insert(insert_index + idx, new_line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print('✅ Successfully added is_new property to Task model')
else:
    print('❌ Could not find insertion point')
