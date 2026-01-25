# Check all template files for tag balance
import re
import os

base_dir = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates'

def check_template(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ifs = len(re.findall(r'{%\s*if\s+', content))
        endifs = len(re.findall(r'{%\s*endif\s*%}', content))
        
        return ifs, endifs, ifs - endifs
    except Exception as e:
        return None, None, str(e)

# Check key templates
templates = [
    'base_complete.html',
    'home_modern.html',
]

print("Template Tag Balance Check:")
print("=" * 60)

for template in templates:
    filepath = os.path.join(base_dir, template)
    ifs, endifs, diff = check_template(filepath)
    
    if diff == 0:
        status = "✓ BALANCED"
    else:
        status = f"✗ UNBALANCED ({diff:+d})"
    
    print(f"{template:30} {ifs:3} if, {endifs:3} endif - {status}")

print("=" * 60)

# Now check the combined rendering
print("\nChecking combined template (base_complete + home_modern)...")
base_path = os.path.join(base_dir, 'base_complete.html')
home_path = os.path.join(base_dir, 'home_modern.html')

with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

with open(home_path, 'r', encoding='utf-8') as f:
    home_content = f.read()

# Simulate Django template inheritance (rough approximation)
# Find {% block content %} in base
block_pattern = r'{%\s*block\s+content\s*%}.*?{%\s*endblock\s*%}'
combined = re.sub(block_pattern, home_content, base_content, flags=re.DOTALL)

ifs = len(re.findall(r'{%\s*if\s+', combined))
endifs = len(re.findall(r'{%\s*endif\s*%}', combined))

print(f"Combined: {ifs} if tags, {endifs} endif tags, diff={ifs-endifs}")

if ifs != endifs:
    print("\n⚠️  PROBLEM FOUND: Combined template has unbalanced tags!")
    print("This explains the Django error.")
else:
    print("\n✓ Combined template is balanced.")
