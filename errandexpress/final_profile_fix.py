
path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\profile.html"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: The specific syntax error reported
bad_syntax = "user.campus_location==value"
good_syntax = "user.campus_location == value"

if bad_syntax in content:
    print(f"Found '{bad_syntax}'. Replacing with '{good_syntax}'...")
    content = content.replace(bad_syntax, good_syntax)
else:
    print(f"'{bad_syntax}' NOT found. Checking manually...")
    # It might be in a different context, let's look for "user.campus_location"
    idx = content.find("user.campus_location")
    if idx != -1:
        print(f"Context: {content[idx:idx+30]}")

# Fix 2: Safety check for other == without spaces in if tags
# This is a simple heuristic, finding "== " is good, "==" is bad if not surrounded by spaces
# But let's just target the specific known issue first to avoid regex complexity unless needed.

# Write back
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("File updated.")
