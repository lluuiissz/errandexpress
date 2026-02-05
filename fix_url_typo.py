
path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\applications.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific typo
new_content = content.replace("url ' task_detail'", "url 'task_detail'")

if new_content != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced content!")
else:
    print("Target string not found.")
    # Debug: print snippet around line 13
    lines = content.splitlines()
    if len(lines) > 13:
        print("Line 13:", lines[12])
