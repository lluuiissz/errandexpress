
import os

filepath = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\task_detail_modern.html'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'accepted_at' in line:
        print(f"Found at line {i+1}: {line.strip()}")
