
path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\profile.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will look for the start of the span and replace until the end of the span.
# Current corrupted state starts with: class="px-4 py-2 rounded-full text-sm font-semibold {% if user.role == 'task_poster' %}Task Poster

# Only replace if we find the specific corrupted line start
corrupted_signature = 'class="px-4 py-2 rounded-full text-sm font-semibold {% if user.role == ' + "'" + 'task_poster' + "'" + ' %}Task Poster'

# The Correct Block
correct_block = """class="px-4 py-2 rounded-full text-sm font-semibold {% if user.role == 'task_poster' %}bg-blue-100 text-blue-800{% elif user.role == 'task_doer' %}bg-green-100 text-green-800{% else %}bg-purple-100 text-purple-800{% endif %}">
                            <i data-lucide="{% if user.role == 'task_poster' %}briefcase{% elif user.role == 'task_doer' %}user-check{% else %}shield{% endif %}"
                                class="w-4 h-4 inline"></i>
                            {% if user.role == 'task_poster' %}Task Poster{% elif user.role == 'task_doer' %}Task Doer{% else %}{{ user.role|title }}{% endif %}"""

if corrupted_signature in content:
    print("Found Corrupted Block. Restoring...")
    # I need to be careful about what I replace.
    # The corrupted line seems to end with ...{% endif %}
    # Check the file view from step 1568. Line 41 ends with {% endif %} then newline.
    
    # I'll simply replace the corrupted line.
    # Since I don't know exactly what follows (it looks like </span> in line 42? No, line 42 IS </span> in file view)
    
    # Let's locate the line in the content
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if corrupted_signature in line:
            # Found it at index i
            # Replace line i with correct_block
            lines[i] = "                            " + correct_block
            break
            
    new_content = '\n'.join(lines)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Restored.")

else:
    print("Could not find corrupted signature. Manual check required.")
