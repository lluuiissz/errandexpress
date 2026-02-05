
import re

file_path = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\templates\base_complete.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Notifications Badge
# Matches the span class line ending in {{, followed by whitespace/newlines, followed by variable }}</span>
# Use DOTALL or explicit [\s\S] not needed if we match newlines
pattern_notifications = r'(class="ml-auto bg-red-500 text-white text-xs px-2 py-0\.5 rounded-full font-semibold">)\s*\{\{\s*\n\s*user_stats\.unread_notifications_count\s*\}\}\s*</span>'
replacement_notifications = r'\1{{ user_stats.unread_notifications_count }}</span>'

# Pattern 2: Messages Badge
pattern_messages = r'(class="ml-auto bg-red-500 text-white text-xs px-2 py-0\.5 rounded-full font-semibold">)\s*\{\{\s*\n\s*user_stats\.unread_messages_count\s*\}\}\s*</span>'
replacement_messages = r'\1{{ user_stats.unread_messages_count }}</span>'

new_content = re.sub(pattern_notifications, replacement_notifications, content, flags=re.MULTILINE)
new_content = re.sub(pattern_messages, replacement_messages, new_content, flags=re.MULTILINE)

if content != new_content:
    print("Found and replaced patterns.")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
else:
    print("Patterns not found or already fixed.")
    # Debug: print snippets to see what's there
    start_idx = content.find('unread_notifications_count')
    if start_idx != -1:
        print(f"Context around unread_notifications_count:\n{content[start_idx-100:start_idx+100]}")
