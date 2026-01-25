
path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\profile.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic string
bad_string = "{% if user.campus_location==value %}"
# The fix
good_string = "{% if user.campus_location == value %}"

if bad_string in content:
    print("Found Error! Fixing...")
    new_content = content.replace(bad_string, good_string)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fix Applied.")
else:
    print("Error string NOT found. Maybe whitespace is different?")
    # Print the specific area to debug
    start = content.find("CAMPUS_CHOICES")
    if start != -1:
        print("Context around CAMPUS_CHOICES:")
        print(content[start:start+200])
