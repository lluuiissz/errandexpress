
import os
import re

file_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\tasks\applications.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # --- FIX 1: URL Spacing Issues ---
    # Replace {% url ' [space] with {% url '
    content = content.replace("{% url ' ", "{% url '")

    # --- FIX 2: Raw Code / Split Template Tags ---
    
    # 1. Match Score split
    # <span class='text-3xl font-extrabold'>{{\s+app.calculated_ranking_score|floatformat:1 }}</span>
    content = re.sub(
        r"(<span class='text-3xl font-extrabold'>)\{\{\s*\n\s*([^}]+)\s*\}\}(</span>)",
        r"\1{{ \2 }}\3",
        content
    )
    
    # 2. Avg Rating split
    # {% if app.current_rating > 0 %}{{ app.current_rating|floatformat:1 }}{% else\s+%}N/A{% endif %}
    content = re.sub(
        r"(\{% else)\s*\n\s*(%\})",
        r" \1 \2",
        content
    )
    
    # 3. Best Review Score split
    # rounded'>{{ \n app.highest_rating.score }}/10</span>
    content = re.sub(
        r"(rounded'>)\{\{\s*\n\s*(app\.highest_rating\.score)\s*\}\}(/10</span>)",
        r"\1{{ \2 }}\3",
        content
    )
    
    # 4. Best Review Feedback split
    # &quot;{{ \n app.highest_rating.feedback|truncatewords:12 }}&quot;
    content = re.sub(
        r"(&quot;)\{\{\s*\n\s*(app\.highest_rating\.feedback\|truncatewords:12)\s*\}\}(&quot;)",
        r"\1{{ \2 }}\3",
        content
    )
    
    # 5. Critical Review Score split
    # rounded'>{{ \n app.lowest_rating.score }}/10</span>
    content = re.sub(
        r"(rounded'>)\{\{\s*\n\s*(app\.lowest_rating\.score)\s*\}\}(/10</span>)",
        r"\1{{ \2 }}\3",
        content
    )
    
    # 6. Critical Review Feedback split
    # &quot;{{ \n app.lowest_rating.feedback|truncatewords:12 }}&quot;
    content = re.sub(
        r"(&quot;)\{\{\s*\n\s*(app\.lowest_rating\.feedback\|truncatewords:12)\s*\}\}(&quot;)",
        r"\1{{ \2 }}\3",
        content
    )

    if content == original_content:
        print("No changes needed - content is already correct.")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully applied ALL fixes (URLs + Raw Code) to applications.html")
        
except Exception as e:
    print(f"Error: {e}")
