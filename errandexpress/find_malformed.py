
import re

filepath = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Scanning for malformed variables...")
for i, line in enumerate(lines):
    # Check for {{ without }}
    if '{{' in line and '}}' not in line:
        print(f"Line {i+1} might be malformed: {line.strip()}")
    # Check for }} without {{
    elif '}}' in line and '{{' not in line:
        print(f"Line {i+1} might be orphaned closing: {line.strip()}")
