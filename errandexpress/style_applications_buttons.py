"""
Add CSS styling to applications page buttons
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\tasks\applications.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("ADDING BUTTON STYLING TO APPLICATIONS PAGE")
print("=" * 70)

# Add CSS at the end before {% endblock %}
css_block = '''
<!-- Button Styling -->
<style>
    /* Enhanced button styles */
    .btn-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transition: all 0.2s ease;
    }
    
    .btn-success:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        transition: all 0.2s ease;
    }
    
    .btn-danger:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        transition: all 0.2s ease;
    }
    
    .btn-secondary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
    }
</style>

{% endblock %}'''

# Replace the closing {% endblock %}
if content.endswith('{% endblock %}\n'):
    content = content[:-14] + css_block
    print("✓ Added CSS styling for buttons")
    
    # Write back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 70)
    print("STYLING APPLIED!")
    print("=" * 70)
    print("\nButtons now have:")
    print("  - Gradient backgrounds")
    print("  - Shadow effects for depth")
    print("  - Hover animations (lift up effect)")
    print("  - Smooth transitions")
else:
    print("⚠ Could not find endblock tag")

print("\n" + "=" * 70)
