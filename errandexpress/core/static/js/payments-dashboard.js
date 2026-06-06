/**
 * 💰 Payments Dashboard JavaScript
 * Handles filtering, search, and payment details
 */

// Filter payments by status
function filterPayments(status) {
    const rows = document.querySelectorAll('.payment-row');
    const buttons = document.querySelectorAll('.filter-btn');

    // Update active button
    buttons.forEach(btn => {
        if (btn.dataset.filter === status) {
            btn.classList.add('active', 'bg-blue-600', 'text-white');
            btn.classList.remove('bg-gray-100', 'text-gray-700');
        } else {
            btn.classList.remove('active', 'bg-blue-600', 'text-white');
            btn.classList.add('bg-gray-100', 'text-gray-700');
        }
    });

    // Filter rows
    rows.forEach(row => {
        const rowStatus = row.dataset.status;
        if (status === 'all' || rowStatus === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Search payments
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-payments');
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('.payment-row');

            rows.forEach(row => {
                const taskName = row.dataset.task;
                if (taskName.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});

// View payment details
async function viewPaymentDetails(paymentId) {
    const modal = document.getElementById('details-modal');
    const content = document.getElementById('details-content');

    // Show loading
    content.innerHTML = `
        <div class="text-center py-8">
            <div class="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p class="text-gray-600">Loading payment details...</p>
        </div>
    `;

    modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/payment-details/${paymentId}/`);
        const data = await response.json();

        if (data.success) {
            const payment = data.payment;
            content.innerHTML = `
                <div class="space-y-4">
                    <!-- Transaction ID -->
                    <div class="bg-gray-50 rounded-lg p-4">
                        <div class="text-sm text-gray-600 mb-1">Transaction ID</div>
                        <div class="font-mono text-sm font-medium text-gray-900">${payment.id}</div>
                    </div>
                    
                    <!-- Task Details -->
                    <div>
                        <div class="text-sm text-gray-600 mb-2">Task</div>
                        <div class="font-semibold text-gray-900">${payment.task_title}</div>
                        <div class="text-sm text-gray-500">${payment.task_location}</div>
                    </div>
                    
                    <!-- Amount Breakdown -->
                    <div class="bg-blue-50 rounded-lg p-4 space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-700">Task Price</span>
                            <span class="font-medium text-gray-900">₱${payment.amount}</span>
                        </div>
                        <div class="flex justify-between items-center text-blue-600">
                            <span class="text-sm">Service Charge (10%)</span>
                            <span class="font-medium">+₱${(parseFloat(payment.amount) * 0.1).toFixed(2)}</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-t border-blue-200 font-bold">
                            <span class="text-gray-900">Total Amount</span>
                            <span class="text-lg text-green-600">₱${(parseFloat(payment.amount) * 1.1).toFixed(2)}</span>
                        </div>
                    </div>
                    
                    <!-- Payment Method -->
                    <div class="flex justify-between items-center">
                        <span class="text-gray-700">Payment Method</span>
                        <span class="font-medium text-gray-900">${payment.method === 'paymongo' ? 'GCash' : 'Cash on Delivery'}</span>
                    </div>
                    
                    <!-- Status -->
                    <div class="flex justify-between items-center">
                        <span class="text-gray-700">Status</span>
                        <span class="px-3 py-1 rounded-full text-sm font-medium ${payment.status === 'confirmed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }">
                            ${payment.status_display}
                        </span>
                    </div>
                    
                    <!-- Date -->
                    <div class="flex justify-between items-center">
                        <span class="text-gray-700">Date</span>
                        <span class="font-medium text-gray-900">${payment.created_at}</span>
                    </div>
                    
                    <!-- Actions -->
                    <div class="pt-4 flex gap-3">
                        <button onclick="window.open('/messages/', '_blank')" 
                                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2">
                            <i data-lucide="message-circle" class="w-4 h-4"></i>
                            <span>View Chat</span>
                        </button>
                        <button onclick="downloadReceipt('${payment.id}')" 
                                class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium flex items-center justify-center gap-2">
                            <i data-lucide="download" class="w-4 h-4"></i>
                            <span>Receipt</span>
                        </button>
                    </div>
                </div>
            `;

            // Reinitialize icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        } else {
            content.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i data-lucide="alert-circle" class="w-8 h-8 text-red-600"></i>
                    </div>
                    <p class="text-gray-900 font-medium mb-2">Failed to load details</p>
                    <p class="text-gray-600 text-sm">${data.message || 'Please try again'}</p>
                </div>
            `;

            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    } catch (error) {
        console.error('Error loading payment details:', error);
        content.innerHTML = `
            <div class="text-center py-8">
                <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i data-lucide="alert-circle" class="w-8 h-8 text-red-600"></i>
                </div>
                <p class="text-gray-900 font-medium mb-2">Error loading details</p>
                <p class="text-gray-600 text-sm">${error.message}</p>
            </div>
        `;

        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function closeDetailsModal() {
    document.getElementById('details-modal').classList.add('hidden');
}

// Download receipt
function downloadReceipt(paymentId) {
    window.open(`/api/download-receipt/${paymentId}/`, '_blank');
}

// Close modals on backdrop click
document.addEventListener('DOMContentLoaded', function () {
    const detailsModal = document.getElementById('details-modal');
    if (detailsModal) {
        detailsModal.addEventListener('click', function (e) {
            if (e.target === this) {
                closeDetailsModal();
            }
        });
    }
});
