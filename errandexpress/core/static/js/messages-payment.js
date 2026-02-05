/**
 * 💬 Messages Payment Handler
 * Handles task payments from messages interface
 */

class MessagesPaymentHandler {
    constructor() {
        this.baseUrl = window.location.origin;
        this.currentTaskId = null;
        this.currentAmount = 0;
        this.selectedMethod = null;
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!token) {
            // Try to get from cookie
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    return value;
                }
            }
        }
        return token || '';
    }

    showToast(message, type = 'success') {
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info';

        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 animate-slide-in`;
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <i data-lucide="${icon}" class="w-6 h-6"></i>
                <div>
                    <div class="font-bold">${message}</div>
                </div>
            </div>
        `;
        document.body.appendChild(toast);

        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    setButtonLoading(isLoading) {
        const btn = document.getElementById('confirm-payment-btn');
        const btnText = document.getElementById('btn-text');
        const btnLoader = document.getElementById('btn-loader');

        if (isLoading) {
            btn.disabled = true;
            btnText.classList.add('hidden');
            btnLoader.classList.remove('hidden');
        } else {
            btn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    }

    // Process GCash payment for task
    async processGCashTaskPayment() {
        try {
            console.log('💳 Processing GCash task payment...');
            this.setButtonLoading(true);

            // Step 1: Complete task and create payment record
            const completeResponse = await fetch(`${this.baseUrl}/api/complete-task-payment/${this.currentTaskId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    payment_method: 'paymongo'
                })
            });

            // Check if response is OK
            if (!completeResponse.ok) {
                const errorData = await completeResponse.json();
                throw new Error(errorData.message || errorData.error || `Server error: ${completeResponse.status}`);
            }

            const completeData = await completeResponse.json();
            console.log('✅ Payment initiation response:', completeData);

            if (!completeData.success) {
                throw new Error(completeData.message || completeData.error || 'Failed to initiate payment');
            }

            const paymentId = completeData.payment_id;

            // Step 2: Create GCash source (skip payment intent for now)
            console.log('💳 Creating GCash source...');
            const gcashResponse = await fetch(`${this.baseUrl}/api/create-task-gcash-payment/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    payment_id: paymentId
                })
            });

            if (!gcashResponse.ok) {
                const errorData = await gcashResponse.json();
                throw new Error(errorData.error || `GCash creation failed: ${gcashResponse.status}`);
            }

            const gcashData = await gcashResponse.json();
            console.log('✅ GCash response:', gcashData);

            if (gcashData.success && gcashData.checkout_url) {
                // Close modal
                closePaymentModal();

                // Show info
                this.showToast('Opening GCash payment...', 'info');

                // Open GCash checkout
                const paymentWindow = window.open(
                    gcashData.checkout_url,
                    'gcash_payment',
                    'width=600,height=700,scrollbars=yes,resizable=yes'
                );

                if (!paymentWindow) {
                    throw new Error('Popup blocked. Please allow popups.');
                }

                // Monitor payment
                this.monitorPaymentWindow(paymentWindow, paymentId);

            } else {
                throw new Error(gcashData.error || 'Failed to create payment');
            }

        } catch (error) {
            console.error('❌ Payment error:', error);
            this.showToast(error.message, 'error');
        } finally {
            this.setButtonLoading(false);
        }
    }

    // Process COD payment
    async processCODTaskPayment() {
        try {
            console.log('💵 Processing COD payment...');
            this.setButtonLoading(true);

            const response = await fetch(`${this.baseUrl}/api/complete-task-payment/${this.currentTaskId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    payment_method: 'cod'
                })
            });

            const data = await response.json();

            if (data.success) {
                closePaymentModal();
                this.showToast('COD payment recorded. Awaiting confirmation.', 'success');

                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                throw new Error(data.message || 'COD payment failed');
            }

        } catch (error) {
            console.error('❌ COD error:', error);
            this.showToast(error.message, 'error');
        } finally {
            this.setButtonLoading(false);
        }
    }

    // Monitor payment window
    monitorPaymentWindow(paymentWindow, paymentId) {
        const checkInterval = setInterval(() => {
            try {
                if (paymentWindow.closed) {
                    clearInterval(checkInterval);
                    console.log('🔍 Payment window closed, checking status...');

                    setTimeout(() => {
                        this.checkTaskPaymentStatus(paymentId);
                    }, 2000);
                }
            } catch (e) {
                console.log('Checking window...');
            }
        }, 1000);

        setTimeout(() => {
            if (!paymentWindow.closed) {
                clearInterval(checkInterval);
                this.checkTaskPaymentStatus(paymentId);
            }
        }, 300000); // 5 minutes
    }

    // Check payment status
    async checkTaskPaymentStatus(paymentId) {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/check-payment-status/?payment_id=${paymentId}`,
                {
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                }
            );

            const data = await response.json();

            if (data.status === 'confirmed') {
                this.showToast('Payment successful! Task completed.', 'success');

                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                this.showToast('Payment pending. Please wait...', 'info');
            }

        } catch (error) {
            console.error('❌ Status check error:', error);
        }
    }
}

// Initialize handler
const messagesPayment = new MessagesPaymentHandler();

// Modal functions
function openPaymentModal(taskId, amount) {
    messagesPayment.currentTaskId = taskId;
    messagesPayment.currentAmount = parseFloat(amount);
    messagesPayment.selectedMethod = null;

    // Calculate Service Fee (Add-On: 10%)
    const taskPrice = messagesPayment.currentAmount;
    const serviceFee = taskPrice * 0.10;
    const totalToPay = taskPrice + serviceFee;

    document.getElementById('modal-amount').textContent = `₱${taskPrice.toFixed(2)}`;
    document.getElementById('modal-service-fee').textContent = `₱${serviceFee.toFixed(2)}`;
    document.getElementById('modal-total').textContent = `₱${totalToPay.toFixed(2)}`;
    document.getElementById('payment-modal').classList.remove('hidden');
    document.getElementById('confirm-payment-btn').disabled = true;

    // Reset payment method buttons
    document.querySelectorAll('.payment-method-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'border-green-500', 'bg-blue-50', 'bg-green-50');
        btn.classList.add('border-gray-200');
        btn.querySelector('.check-icon').classList.add('hidden');
    });

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closePaymentModal() {
    document.getElementById('payment-modal').classList.add('hidden');
}

function selectPaymentMethod(method) {
    messagesPayment.selectedMethod = method;

    // Update UI
    document.querySelectorAll('.payment-method-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'border-green-500', 'bg-blue-50', 'bg-green-50');
        btn.classList.add('border-gray-200');
        btn.querySelector('.check-icon').classList.add('hidden');
    });

    const selectedBtn = event.currentTarget;
    let color = 'blue';
    if (method === 'gcash') color = 'blue';
    else if (method === 'cod') color = 'green';

    selectedBtn.classList.remove('border-gray-200');
    selectedBtn.classList.add(`border-${color}-500`, `bg-${color}-50`);
    selectedBtn.querySelector('.check-icon').classList.remove('hidden');

    // Enable confirm button
    document.getElementById('confirm-payment-btn').disabled = false;

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function processTaskPayment() {
    if (messagesPayment.selectedMethod === 'gcash') {
        messagesPayment.processGCashTaskPayment();
    } else if (messagesPayment.selectedMethod === 'cod') {
        messagesPayment.processCODTaskPayment();
    }
}

// Close modal on backdrop click
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('payment-modal');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === this) {
                closePaymentModal();
            }
        });
    }
});
