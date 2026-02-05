
import os
import re

filepath = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the specific split if tag
# {% if existing_payment and existing_payment.status == 'pending_confirmation' and \n existing_payment.method == 'cod' %}
# We'll use a regex that matches the first part and second part with flexible whitespace
pattern = r'(\{%\s*if existing_payment and existing_payment\.status == \'pending_confirmation\' and)\s*\n\s*(existing_payment\.method == \'cod\'\s*%\})'

match = re.search(pattern, content)
if match:
    print("Found split tag!")
    replacement = match.group(1) + " " + match.group(2)
    # also clean up any potential double spaces if needed, but simple join is safer
    replacement = re.sub(r'\s+', ' ', replacement)
    # Restore the {% start
    replacement = replacement.replace("{% ", "{% ")
    
    # Actually, simpler: just literal replace of the lines we know
    
    # Let's try to construct the exact string we saw in find_line output to be safe
    # But regex is better for handling the newline
    
    new_content = re.sub(pattern, lambda m: m.group(1) + " " + m.group(2), content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed split tag.")
else:
    print("Could not find split tag with regex.")
    # Fallback: try to find the rough string
    if "pending_confirmation' and\n" in content:
         print("Found newline substring method")
    
