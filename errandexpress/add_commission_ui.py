"""
Add Commission Payment UI to Chat Page
"""

template_path = r'c:\Users\Admin\Desktop\errandexpress\errandexpress\core\templates\chat_modern.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("ADDING COMMISSION PAYMENT UI TO CHAT PAGE")
print("=" * 70)

# Commission Payment Overlay HTML
commission_ui = '''
            <!-- Commission Payment Overlay (shown when commission not paid) -->
            <div id="commission-paywall-overlay"
                class="hidden absolute inset-0 bg-white/95 backdrop-blur-sm z-30 flex items-center justify-center">
                <div class="text-center p-8 max-w-md">
                    <div
                        class="w-20 h-20 bg-gradient-to-r from-amber-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i data-lucide="credit-card" class="w-10 h-10 text-white"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-gray-900 mb-2">💳 Commission Payment Required</h3>
                    <p class="text-gray-600 mb-4">
                        To continue chatting, please pay the <strong class="text-amber-600">₱10.00 commission fee</strong>.<br>
                        This is a one-time payment for this task.
                    </p>

                    <!-- Benefits -->
                    <div class="bg-amber-50 rounded-xl p-4 mb-6 text-left">
                        <p class="text-sm font-semibold text-gray-900 mb-2">✨ What you get:</p>
                        <ul class="text-sm text-gray-700 space-y-1">
                            <li class="flex items-center gap-2">
                                <i data-lucide="check" class="w-4 h-4 text-green-600"></i>
                                Unlock unlimited messaging
                            </li>
                            <li class="flex items-center gap-2">
                                <i data-lucide="check" class="w-4 h-4 text-green-600"></i>
                                File sharing & attachments
                            </li>
                            <li class="flex items-center gap-2">
                                <i data-lucide="check" class="w-4 h-4 text-green-600"></i>
                                Real-time collaboration
                            </li>
                            <li class="flex items-center gap-2">
                                <i data-lucide="check" class="w-4 h-4 text-green-600"></i>
                                One-time payment per task
                            </li>
                        </ul>
                    </div>

                    <button onclick="payCommission()"
                        class="w-full px-6 py-4 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-xl hover:shadow-lg transition-all font-semibold text-lg flex items-center justify-center gap-2">
                        <i data-lucide="credit-card" class="w-5 h-5"></i>
                        <span>Pay Commission - ₱10.00</span>
                    </button>

                    <p class="text-xs text-gray-500 mt-3">
                        💳 Pay via GCash or Cash on Delivery
                    </p>
                </div>
            </div>
'''

# Find where to insert (after the paywall-overlay div, before {% endif %})
insertion_point = content.find('</div>\n            {% endif %}\n        </div>')

if insertion_point > 0:
    content = content[:insertion_point] + '</div>\n' + commission_ui + '\n            {% endif %}\n        </div>' + content[insertion_point + len('</div>\n            {% endif %}\n        </div>'):]
    print("✓ Added commission payment overlay UI")
    
    # Write back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 70)
    print("COMMISSION PAYMENT UI ADDED!")
    print("=" * 70)
    print("\nNew UI includes:")
    print("  ✓ Prominent commission payment overlay")
    print("  ✓ Clear ₱10.00 commission amount")
    print("  ✓ Benefits list")
    print("  ✓ 'Pay Commission' button")
    print("  ✓ Payment method info (GCash/COD)")
else:
    print("⚠ Could not find insertion point")

print("\n" + "=" * 70)
