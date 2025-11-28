/**
 * 💸 PAYMONGO LIVE INTEGRATION - Frontend Implementation
 * Handles ₱2 system fee payment with GCash
 * PRODUCTION READY WITH LIVE KEYS
 */

class PayMongoLive {
    constructor() {
        this.baseUrl = window.location.origin;
        this.init();
    }
    
    init() {
        // Set up payment buttons
        this.setupPaymentButtons();
        
        // Handle payment success/failure redirects
        this.handlePaymentRedirects();
    }
    
    setupPaymentButtons() {
        // Find all "Pay ₱2 Fee" buttons
        const payButtons = document.querySelectorAll('[data-pay-fee]');
        
        payButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                
                const taskId = button.dataset.taskId;
                if (!taskId) {
                    this.showError('Task ID not found');
                    return;
                }
                
                // Get selected payment method from form
                const paymentMethodRadio = document.querySelector('input[name="payment_method"]:checked');
                const paymentMethod = paymentMethodRadio ? paymentMethodRadio.value : 'gcash';
                
                await this.processPayment(taskId, button, paymentMethod);
            });
        });
    }
    
    async processPayment(taskId, button, paymentMethod = 'gcash') {
        try {
            // Show loading state
            this.setButtonLoading(button, true);
            this.showInfo('Creating payment link...');
            
            // Step 1: Create payment intent
            console.log('Creating payment intent for task:', taskId, 'Method:', paymentMethod);
            const intentResponse = await fetch(`${this.baseUrl}/api/create-payment-intent/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ 
                    task_id: taskId,
                    payment_method: paymentMethod
                })
            });
            
            console.log('Intent response status:', intentResponse.status);
            
            if (!intentResponse.ok) {
                const errorText = await intentResponse.text();
                console.error('Intent response error:', errorText);
                throw new Error(`Failed to create payment intent: ${intentResponse.status}`);
            }
            
            const intentData = await intentResponse.json();
            console.log('Payment intent response:', intentData);
            
            // Validate response structure - check all possible structures
            if (!intentData) {
                throw new Error('Empty response from payment intent API');
            }
            
            // Check if this is a card form response
            if (intentData.is_card_form) {
                console.log('Card form detected, redirecting to form page');
                // Handle card form - no client_key needed
                if (intentData.success && intentData.checkout_url) {
                    this.showSuccess('Opening card payment form...');
                    window.location.href = intentData.checkout_url;
                    return;  // Exit early - don't continue with GCash flow
                }
            }
            
            // Try to extract client_key from different possible response structures
            let clientKey = null;
            
            // Structure 1: { data: { attributes: { client_key: ... } } }
            if (intentData.data && intentData.data.attributes && intentData.data.attributes.client_key) {
                clientKey = intentData.data.attributes.client_key;
                console.log('Found client_key in data.attributes');
            }
            // Structure 2: { data: { id: ..., client_key: ... } }
            else if (intentData.data && intentData.data.client_key) {
                clientKey = intentData.data.client_key;
                console.log('Found client_key in data');
            }
            // Structure 3: Direct client_key
            else if (intentData.client_key) {
                clientKey = intentData.client_key;
                console.log('Found client_key at root');
            }
            
            if (!clientKey) {
                console.error('Response structure:', JSON.stringify(intentData, null, 2));
                throw new Error('No client_key found in payment intent response. Check console for response structure.');
            }
            
            console.log('Using client_key:', clientKey);
            
            // Step 2: Create payment source (GCash or Card)
            console.log('Creating payment source...');
            
            // Use selected payment method
            const endpoint = paymentMethod === 'gcash' ? '/api/create-gcash-payment/' : '/api/create-card-payment/';
            
            const paymentResponse = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ 
                    task_id: taskId,
                    client_key: clientKey
                })
            });
            
            console.log('Payment response status:', paymentResponse.status);
            
            if (!paymentResponse.ok) {
                const errorText = await paymentResponse.text();
                console.error('Payment response error:', errorText);
                throw new Error(`Failed to create payment: ${paymentResponse.status}`);
            }
            
            const paymentData = await paymentResponse.json();
            console.log('Payment response:', paymentData);
            
            if (paymentData.success && paymentData.checkout_url) {
                // Check if this is a card form (not a checkout URL)
                if (paymentData.is_card_form) {
                    // For card form, redirect to the form page
                    this.showSuccess('Opening card payment form...');
                    window.location.href = paymentData.checkout_url;
                } else {
                    // For GCash, open checkout in new window
                    const methodDisplay = paymentMethod === 'gcash' ? 'GCash' : 'Card';
                    this.showSuccess(`Opening ${methodDisplay} payment...`);
                    
                    const paymentWindow = window.open(
                        paymentData.checkout_url, 
                        'payment_checkout',
                        'width=600,height=700,scrollbars=yes,resizable=yes'
                    );
                    
                    // Monitor payment window
                    this.monitorPaymentWindow(paymentWindow, taskId);
                }
                
            } else {
                throw new Error(paymentData.error || 'Failed to get checkout URL');
            }
            
        } catch (error) {
            console.error('Payment error:', error);
            console.error('Error stack:', error.stack);
            this.showError(`Payment failed: ${error.message}`);
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    monitorPaymentWindow(paymentWindow, taskId) {
        const checkClosed = setInterval(() => {
            if (paymentWindow.closed) {
                clearInterval(checkClosed);
                
                // Check payment status after window closes
                setTimeout(() => {
                    this.checkPaymentStatus(taskId);
                }, 2000);
            }
        }, 1000);
        
        // Auto-close after 10 minutes
        setTimeout(() => {
            if (!paymentWindow.closed) {
                paymentWindow.close();
                clearInterval(checkClosed);
                this.showWarning('Payment window closed. Please check your payment status.');
            }
        }, 600000); // 10 minutes
    }
    
    async checkPaymentStatus(taskId) {
        try {
            this.showInfo('Checking payment status...');
            
            const response = await fetch(`${this.baseUrl}/api/check-chat/${taskId}/`);
            const data = await response.json();
            
            if (data.allowed) {
                this.showSuccess('✅ Payment confirmed! Chat unlocked.');
                
                // Hide payment modal and refresh chat UI instead of full page reload
                const modal = document.getElementById('payment-modal');
                if (modal) {
                    modal.classList.add('hidden');
                }
                
                // Refresh input area to show unlocked state
                const inputWrapper = document.getElementById('message-input-wrapper');
                if (inputWrapper) {
                    // Reload just the input section
                    fetch(`${this.baseUrl}/messages/${taskId}/`)
                        .then(r => r.text())
                        .then(html => {
                            const parser = new DOMParser();
                            const newDoc = parser.parseFromString(html, 'text/html');
                            const newInput = newDoc.getElementById('message-input-wrapper');
                            if (newInput) {
                                inputWrapper.innerHTML = newInput.innerHTML;
                                // Re-initialize Lucide icons
                                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                                    lucide.createIcons();
                                }
                            }
                        });
                }
                
            } else if (data.payment_required) {
                this.showWarning('Payment not yet confirmed. Please try again or contact support.');
            }
            
        } catch (error) {
            console.error('Status check error:', error);
            this.showError('Unable to verify payment status');
        }
    }
    
    handlePaymentRedirects() {
        const urlParams = new URLSearchParams(window.location.search);
        const taskId = urlParams.get('task_id');
        
        if (window.location.pathname.includes('/payment/success/') && taskId) {
            this.showSuccess('🎉 Payment successful! Chat will be unlocked shortly.');
            
            // Check status and redirect
            setTimeout(() => {
                this.checkPaymentStatus(taskId);
            }, 3000);
            
        } else if (window.location.pathname.includes('/payment/failed/') && taskId) {
            this.showError('❌ Payment failed. Please try again.');
        }
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i data-lucide="loader" class="w-5 h-5 inline mr-2"></i>Processing...';
            button.classList.add('btn-loading');
        } else {
            button.disabled = false;
            // Restore original button text
            const originalText = button.getAttribute('data-original-text') || 'Pay ₱2 via GCash';
            button.innerHTML = '<i data-lucide="credit-card" class="w-5 h-5 inline mr-2"></i>' + originalText;
            button.classList.remove('btn-loading');
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showWarning(message) {
        this.showNotification(message, 'warning');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existing = document.querySelectorAll('.paymongo-notification');
        existing.forEach(n => n.remove());
        
        // Create new notification
        const notification = document.createElement('div');
        notification.className = `paymongo-notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds (except errors)
        if (type !== 'error') {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 5000);
        }
    }
}

// Auto-initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.payMongoLive = new PayMongoLive();
});

// Add CSS for notifications and loading states
const payMongoCSS = `
.paymongo-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    animation: slideInRight 0.3s ease;
    max-width: 400px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.notification-success { background: #28a745; }
.notification-error { background: #dc3545; }
.notification-warning { background: #ffc107; color: #212529; }
.notification-info { background: #17a2b8; }

.notification-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.notification-close {
    background: none;
    border: none;
    color: inherit;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-loading {
    opacity: 0.7;
    cursor: not-allowed !important;
    position: relative;
}

.btn-loading::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    margin: auto;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
}

@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Payment button styles */
[data-pay-fee] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
}

[data-pay-fee]:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(102, 126, 234, 0.4);
}

[data-pay-fee]:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = payMongoCSS;
document.head.appendChild(style);
