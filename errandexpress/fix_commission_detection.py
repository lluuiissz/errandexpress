"""
Modify chat JavaScript to show commission overlay on commission error
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\chat_modern.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("MODIFYING JAVASCRIPT TO AUTO-SHOW COMMISSION OVERLAY")
print("=" * 70)

# Find and replace the sendMessage function to detect commission error
old_code = '''        // Check message limit BEFORE doing anything
        if (!canSendMessage()) {
            showToast('Message limit reached. Please pay ₱2 system fee to continue chatting.', 'warning');
            // Show payment modal
            const paywallOverlay = document.getElementById('paywall-overlay');
            if (paywallOverlay) {
                paywallOverlay.classList.remove('hidden');
            }
            return;
        }'''

new_code = '''        // Check message limit BEFORE doing anything
        if (!canSendMessage()) {
            showToast('Message limit reached. Please pay ₱2 system fee to continue chatting.', 'warning');
            // Show payment modal
            const paywallOverlay = document.getElementById('paywall-overlay');
            if (paywallOverlay) {
                paywallOverlay.classList.remove('hidden');
            }
            return;
        }'''

# Add a global error handler for commission errors
commission_handler = '''
    // Global handler for commission payment errors
    window.addEventListener('DOMContentLoaded', function() {
        // Check if there's a commission error in messages
        const djangoMessages = document.querySelectorAll('.django-message');
        djangoMessages.forEach(msg => {
            const messageText = msg.getAttribute('data-message');
            if (messageText && (messageText.includes('₱10') || messageText.includes('commission'))) {
                // Show commission overlay
                showCommissionPaywall();
            }
        });
    });

    // Override showToast to detect commission errors
    const originalShowToast = window.showToast;
    if (originalShowToast) {
        window.showToast = function(message, type) {
            if (message && (message.includes('₱10') || message.includes('commission'))) {
                showCommissionPaywall();
            } else {
                originalShowToast(message, type);
            }
        };
    }

'''

# Insert after the DOMContentLoaded event listener
insertion_point = content.find('    // Initialize on page load\n    document.addEventListener(\'DOMContentLoaded\', function () {')

if insertion_point > 0:
    # Find the end of that DOMContentLoaded block
    end_point = content.find('    });', insertion_point) + 7
    content = content[:end_point] + '\n' + commission_handler + content[end_point:]
    print("✓ Added commission error detection handler")
    print("✓ Modified showToast to detect commission errors")
    
    # Write back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 70)
    print("JAVASCRIPT UPDATED!")
    print("=" * 70)
    print("\nChanges made:")
    print("  ✓ Auto-detects commission error messages")
    print("  ✓ Shows commission overlay automatically")
    print("  ✓ Intercepts toast notifications for commission errors")
else:
    print("⚠ Could not find insertion point")

print("\n" + "=" * 70)
