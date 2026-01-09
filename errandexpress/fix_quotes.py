# Fix smart quotes in template
file_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\browse_tasks_modern.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace smart quotes with regular quotes
fixed_content = content.replace(''', "'").replace(''', "'").replace('"', '"').replace('"', '"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('✅ Fixed all smart quotes in template')
