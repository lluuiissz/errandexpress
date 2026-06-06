
import os

filepath = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i in range(len(lines)):
    if skip_next:
        skip_next = False
        continue
        
    line = lines[i]
    # Check for line 339 (index 338) and 340 (index 339) roughly by content if line numbers shifted
    # We look for the split date filter pattern
    
    if '{{ task.accepted_at|date:"M d, Y" }} &bull; {{' in line and (i + 1 < len(lines)):
        next_line = lines[i+1]
        if 'task.accepted_at|date:"g:i A" }}' in next_line:
            # Join them
            joined = line.strip() + " " + next_line.strip() + "\n"
            # Add indentation
            joined = "                                " + joined
            # Replace double spaces if any from join
            # But strip() removed existing indentation, so we add ours.
            # actually better to just construct it
            joined = '                                <p class="text-sm text-gray-500 mt-1">{{ task.accepted_at|date:"M d, Y" }} &bull; {{ task.accepted_at|date:"g:i A" }}</p>\n'
            new_lines.append(joined)
            skip_next = True
            print("Fixed split date filter.")
            continue
            
    # Also check if just <p tag is confusing it
    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
