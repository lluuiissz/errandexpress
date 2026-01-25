"""
Add CSS styling to task application form
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\tasks\apply.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("ADDING FORM STYLING TO TASK APPLICATION PAGE")
print("=" * 70)

# Add CSS before the script tag
css_block = '''
<!-- Form Input Styling -->
<style>
    /* Style form inputs for better visual appeal */
    textarea, input[type="text"] {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 2px solid #e5e7eb;
        border-radius: 0.75rem;
        font-family: inherit;
        font-size: 1rem;
        transition: all 0.2s ease;
        background-color: #ffffff;
    }
    
    textarea:focus, input[type="text"]:focus {
        outline: none;
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    textarea {
        min-height: 150px;
        resize: vertical;
    }
    
    /* Enhanced submit button */
    .btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        transition: all 0.2s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
    }
</style>

'''

# Insert before the script tag
if '<!-- Character Counter Script -->' in content:
    content = content.replace('<!-- Character Counter Script -->', css_block + '<!-- Character Counter Script -->')
    print("✓ Added CSS styling for form inputs")
    print("✓ Enhanced submit button styling")
    
    # Write back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 70)
    print("STYLING APPLIED!")
    print("=" * 70)
    print("\nForm inputs now have:")
    print("  - Rounded borders with focus effects")
    print("  - Smooth transitions")
    print("  - Enhanced submit button with gradient and shadow")
else:
    print("⚠ Could not find insertion point")

print("\n" + "=" * 70)
