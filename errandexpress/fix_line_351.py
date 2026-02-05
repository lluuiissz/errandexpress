import re

file_path = r'c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\task_detail_modern.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the split if tag at line 351-352
# Match the pattern across lines with any whitespace/newline
pattern = r"{% if existing_payment and existing_payment\.status == 'pending_confirmation' and\s*\r?\n\s*existing_payment\.method == 'cod' %}"
replacement = "{% if existing_payment and existing_payment.status == 'pending_confirmation' and existing_payment.method == 'cod' %}"

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    print("✅ Fixed split tag at line 351-352")
else:
    print("⚠️  Pattern not found - tag may already be fixed")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File updated successfully!")
