"""
Professional redesign of applications page
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\tasks\applications.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("APPLYING PROFESSIONAL REDESIGN TO APPLICATIONS PAGE")
print("=" * 70)

# Professional CSS redesign
professional_css = '''
<!-- Professional Redesign Styling -->
<style>
    /* Professional color scheme */
    :root {
        --primary-blue: #2563eb;
        --primary-blue-dark: #1e40af;
        --success-green: #16a34a;
        --success-green-dark: #15803d;
        --danger-red: #dc2626;
        --danger-red-dark: #b91c1c;
        --neutral-gray: #64748b;
        --neutral-gray-dark: #475569;
        --bg-light: #f8fafc;
        --border-light: #e2e8f0;
    }
    
    /* Clean card styling */
    .card {
        background: white;
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    
    /* Professional buttons */
    .btn {
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 0.875rem;
        border-radius: 8px;
        transition: all 0.15s ease;
        border: none;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
    }
    
    .btn-success {
        background-color: var(--success-green);
        color: white;
    }
    
    .btn-success:hover {
        background-color: var(--success-green-dark);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(22, 163, 74, 0.2);
    }
    
    .btn-danger {
        background-color: var(--danger-red);
        color: white;
    }
    
    .btn-danger:hover {
        background-color: var(--danger-red-dark);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(220, 38, 38, 0.2);
    }
    
    .btn-secondary {
        background-color: white;
        color: var(--neutral-gray);
        border: 1px solid var(--border-light);
    }
    
    .btn-secondary:hover {
        background-color: var(--bg-light);
        border-color: #cbd5e1;
    }
    
    /* Professional badges */
    .badge {
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
    }
    
    .badge-success {
        background-color: #dcfce7;
        color: var(--success-green-dark);
    }
    
    .badge-purple {
        background-color: #f3e8ff;
        color: #7c3aed;
    }
    
    /* Stats grid styling */
    .bg-gray-50 {
        background-color: var(--bg-light);
        border: 1px solid var(--border-light);
    }
    
    /* Ranking score box */
    .bg-gradient-to-r {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
    }
    
    /* Info boxes */
    .bg-blue-50 {
        background-color: #eff6ff;
        border-color: #bfdbfe;
    }
    
    /* Typography improvements */
    h1, h2, h3, h4 {
        color: #0f172a;
        letter-spacing: -0.025em;
    }
    
    .text-muted {
        color: var(--neutral-gray);
    }
    
    /* Newbie border highlight */
    .border-purple-200 {
        border-color: #e9d5ff !important;
        background-color: #faf5ff;
    }
</style>

{% endblock %}'''

# Replace the existing style block and endblock
if '<!-- Button Styling -->' in content:
    # Remove old styling
    start = content.find('<!-- Button Styling -->')
    end = content.find('{% endblock %}', start) + 14
    content = content[:start] + professional_css
    print("✓ Replaced old styling with professional redesign")
elif content.endswith('{% endblock %}\n'):
    content = content[:-14] + professional_css
    print("✓ Added professional styling")
else:
    print("⚠ Could not find insertion point")
    
# Write back
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("PROFESSIONAL REDESIGN COMPLETE!")
print("=" * 70)
print("\nNew design features:")
print("  ✓ Clean, corporate color scheme")
print("  ✓ Refined button styling with subtle shadows")
print("  ✓ Professional typography")
print("  ✓ Improved card hover effects")
print("  ✓ Consistent spacing and borders")
print("  ✓ Modern badge designs")
print("\n" + "=" * 70)
