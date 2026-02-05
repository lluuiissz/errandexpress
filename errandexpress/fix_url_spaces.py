
import os

file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\applications.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all occurrences of the malformed URL tag
    # specifically {% url ' task_detail', {% url ' accept_application', etc.
    # The pattern seems to be generally {% url ' [space]
    
    new_content = content.replace("{% url ' ", "{% url '")
    
    if content == new_content:
        print("No changes needed - patterns not found or already fixed.")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated applications.html")
        
except Exception as e:
    print(f"Error: {e}")
