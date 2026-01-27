import os
import re

file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\admin\dashboard.html"

try:
    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the pattern for the specific split tag we keep seeing
    # {% if method.payment_method == 'cod' %}Cash on Delivery (COD){% else %}Online Payment (GCash){%
    # endif %}
    
    # We'll use a regex to match the split and replace with single line
    pattern = r"({% if method\.payment_method == 'cod' %}.*?){%\s*\n\s*endif %}"
    
    # Replacement: ensure it ends with {% endif %} on same line
    def replace_func(match):
        print("Found matching split tag! Joining...")
        group1 = match.group(1)
        return group1 + "{% endif %}"

    new_content, count = re.subn(pattern, replace_func, content, flags=re.DOTALL)

    if count > 0:
        print(f"Fixed {count} split tags.")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("File saved.")
    else:
        print("No split tags matched the pattern. Dumping snippet for debug:")
        # Find matches for "payment_method == 'cod'"
        idx = content.find("payment_method == 'cod'")
        if idx != -1:
            print(content[idx:idx+200])
        else:
            print("Could not find payment_method logic at all.")

except Exception as e:
    print(f"Error: {e}")
