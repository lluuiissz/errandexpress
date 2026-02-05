
import os
import re

file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\my_tasks_modern.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Fix Deadline split
    # Pattern: {{ task.deadline|date:"M\n d, Y" }}
    content = re.sub(
        r"(\{\{ task\.deadline\|date:\"M)\s*\n\s*(d, Y\" \}\})",
        r"\1 \2",
        content
    )

    if content == original_content:
        print("No changes needed - pattern not found.")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully fixed split deadline tag in my_tasks_modern.html")
        
except Exception as e:
    print(f"Error: {e}")
