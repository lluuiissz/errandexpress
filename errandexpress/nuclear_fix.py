
import os

file_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\browse_tasks_modern.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the bad blocks exactly as they appear in the file (based on view_file output)
# Note: Indentation must match exactly.

bad_category_block = """                                <option value="typing" {% if filter_form.category.value=='typing' %}selected{% endif %}>
                                    ⌨️ Typing</option>
                                <option value="powerpoint" {% if filter_form.category.value=='powerpoint' %}selected{%
                                    endif %}>📊 PowerPoint</option>
                                <option value="graphics" {% if filter_form.category.value=='graphics' %}selected{% endif
                                    %}>🎨 Graphics</option>
                                <option value="research" {% if filter_form.category.value=='research' %}selected{% endif
                                    %}>📚 Research</option>
                                <option value="other" {% if filter_form.category.value=='other' %}selected{% endif %}>📌
                                    Other</option>"""

good_category_block = """                                <option value="typing" {% if filter_form.category.value == 'typing' %}selected{% endif %}>⌨️ Typing</option>
                                <option value="powerpoint" {% if filter_form.category.value == 'powerpoint' %}selected{% endif %}>📊 PowerPoint</option>
                                <option value="graphics" {% if filter_form.category.value == 'graphics' %}selected{% endif %}>🎨 Graphics</option>
                                <option value="research" {% if filter_form.category.value == 'research' %}selected{% endif %}>📚 Research</option>
                                <option value="other" {% if filter_form.category.value == 'other' %}selected{% endif %}>📌 Other</option>"""

bad_sort_block = """                                <option value="-created_at" {% if filter_form.sort_by.value=='-created_at' %}selected{%
                                    endif %}>🆕 Newest First</option>
                                <option value="price" {% if filter_form.sort_by.value=='price' %}selected{% endif %}>💰
                                    Price: Low → High</option>
                                <option value="-price" {% if filter_form.sort_by.value=='-price' %}selected{% endif %}>
                                    💎 Price: High → Low</option>
                                <option value="deadline" {% if filter_form.sort_by.value=='deadline' %}selected{% endif
                                    %}>⏰ Deadline: Soonest</option>"""

good_sort_block = """                                <option value="-created_at" {% if filter_form.sort_by.value == '-created_at' %}selected{% endif %}>🆕 Newest First</option>
                                <option value="price" {% if filter_form.sort_by.value == 'price' %}selected{% endif %}>💰 Price: Low → High</option>
                                <option value="-price" {% if filter_form.sort_by.value == '-price' %}selected{% endif %}>💎 Price: High → Low</option>
                                <option value="deadline" {% if filter_form.sort_by.value == 'deadline' %}selected{% endif %}>⏰ Deadline: Soonest</option>"""

# Normalize parsing to avoid newline issues?
# Try direct replacement first. 
# If exact match fails, we might need to be smarter, but let's try this.

def replace_block(text, bad, good):
    if bad in text:
        print("Found bad block, replacing...")
        return text.replace(bad, good)
    else:
        print("WARNING: Bad block not found exactly. Trying relaxed match...")
        # Relaxed match: remove all whitespace from comparison
        # This is risky, let's just print failure
        print("Failure to match block:")
        print(repr(bad[:50]) + "...")
        return text

new_content = replace_block(content, bad_category_block, good_category_block)
new_content = replace_block(new_content, bad_sort_block, good_sort_block)

if content != new_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File updated successfully.")
else:
    print("No changes were made.")
