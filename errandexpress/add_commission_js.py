"""
Add payCommission JavaScript function to chat page
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\chat_modern.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("ADDING COMMISSION PAYMENT JAVASCRIPT FUNCTION")
print("=" * 70)

# JavaScript function
js_function = '''
    // Commission payment function
    function payCommission() {
        // Redirect to commission payment page
        window.location.href = `/payment/commission/${taskId}/`;
    }

    // Show commission paywall when needed
    function showCommissionPaywall() {
        const commissionOverlay = document.getElementById('commission-paywall-overlay');
        if (commissionOverlay) {
            commissionOverlay.classList.remove('hidden');
            // Disable input
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            if (messageInput) messageInput.disabled = true;
            if (sendButton) sendButton.disabled = true;
        }
    }

'''

# Find where to insert (after unlockChat function)
insertion_point = content.find('    // Character counter for textarea')

if insertion_point > 0:
    content = content[:insertion_point] + js_function + '\n    ' + content[insertion_point:]
    print("✓ Added payCommission() JavaScript function")
    print("✓ Added showCommissionPaywall() helper function")
    
    # Write back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 70)
    print("JAVASCRIPT FUNCTIONS ADDED!")
    print("=" * 70)
    print("\nFunctions added:")
    print("  ✓ payCommission() - Redirects to /payment/commission/{task_id}/")
    print("  ✓ showCommissionPaywall() - Shows commission overlay")
else:
    print("⚠ Could not find insertion point")

print("\n" + "=" * 70)
