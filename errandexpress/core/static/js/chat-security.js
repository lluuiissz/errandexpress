/**
 * 💬 CHAT LOCK / UNLOCK ALGORITHM - Frontend Implementation
 * Handles chat access control and payment verification
 */

class ChatSecurity {
    constructor(taskId) {
        this.taskId = taskId;
        this.chatInput = document.getElementById('chat-input');
        this.chatSendBtn = document.getElementById('chat-send-btn');
        this.chatContainer = document.getElementById('chat-container');
        this.paymentAlert = document.getElementById('payment-alert');
        
        this.init();
    }
    
    async init() {
        // Check chat access on page load
        await this.checkChatAccess();
        
        // Set up real-time payment status updates
        this.setupPaymentStatusListener();
        
        // Prevent message sending if chat is locked
        this.setupMessageInterception();
    }
    
    async checkChatAccess() {
        try {
            const response = await fetch(`/api/check-chat/${this.taskId}/`);
            const data = await response.json();
            
            if (data.allowed) {
                this.unlockChat();
            } else {
                this.lockChat(data.reason, data.payment_required);
            }
            
        } catch (error) {
            console.error('Chat access check failed:', error);
            this.lockChat('Unable to verify chat access');
        }
    }
    
    lockChat(reason, paymentRequired = false) {
        // Disable chat input
        if (this.chatInput) {
            this.chatInput.disabled = true;
            this.chatInput.placeholder = reason;
        }
        
        if (this.chatSendBtn) {
            this.chatSendBtn.disabled = true;
        }
        
        // Show payment alert if needed
        if (paymentRequired && this.paymentAlert) {
            this.paymentAlert.style.display = 'block';
            this.paymentAlert.innerHTML = `
                <div class="alert alert-warning">
                    <h5>💳 Payment Required</h5>
                    <p>${reason}</p>
                    <a href="/payment/system-fee/${this.taskId}/" class="btn btn-primary">
                        Pay ₱2 System Fee
                    </a>
                </div>
            `;
        }
        
        // Add visual lock indicator
        if (this.chatContainer) {
            this.chatContainer.classList.add('chat-locked');
        }
    }
    
    unlockChat() {
        // Enable chat input
        if (this.chatInput) {
            this.chatInput.disabled = false;
            this.chatInput.placeholder = 'Type your message...';
        }
        
        if (this.chatSendBtn) {
            this.chatSendBtn.disabled = false;
        }
        
        // Hide payment alert
        if (this.paymentAlert) {
            this.paymentAlert.style.display = 'none';
        }
        
        // Remove visual lock indicator
        if (this.chatContainer) {
            this.chatContainer.classList.remove('chat-locked');
        }
        
        // Show success notification
        this.showNotification('✅ Chat unlocked! You can now send messages.', 'success');
    }
    
    setupPaymentStatusListener() {
        // Poll for payment status updates every 10 seconds
        setInterval(async () => {
            await this.checkChatAccess();
        }, 10000);
        
        // Listen for PayMongo webhook events (if using WebSockets)
        if (window.WebSocket) {
            this.setupWebSocketListener();
        }
    }
    
    setupWebSocketListener() {
        // This would connect to a WebSocket for real-time updates
        // For now, we'll use polling, but this is where you'd add WebSocket logic
        console.log('WebSocket listener setup (placeholder)');
    }
    
    setupMessageInterception() {
        // Intercept form submission
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', async (e) => {
                // Check access before allowing message send
                const accessCheck = await this.checkChatAccessSync();
                if (!accessCheck.allowed) {
                    e.preventDefault();
                    this.showNotification(accessCheck.reason, 'error');
                    return false;
                }
            });
        }
        
        // Intercept send button clicks
        if (this.chatSendBtn) {
            this.chatSendBtn.addEventListener('click', async (e) => {
                const accessCheck = await this.checkChatAccessSync();
                if (!accessCheck.allowed) {
                    e.preventDefault();
                    this.showNotification(accessCheck.reason, 'error');
                    return false;
                }
            });
        }
    }
    
    async checkChatAccessSync() {
        try {
            const response = await fetch(`/api/check-chat/${this.taskId}/`);
            return await response.json();
        } catch (error) {
            return { allowed: false, reason: 'Connection error' };
        }
    }
    
    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                ${message}
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
}

// Auto-initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get task ID from page (you'll need to add this to your templates)
    const taskId = document.querySelector('[data-task-id]')?.dataset.taskId;
    
    if (taskId) {
        window.chatSecurity = new ChatSecurity(taskId);
    }
});

// CSS for chat locking (add to your main.css)
const chatSecurityCSS = `
.chat-locked {
    opacity: 0.6;
    pointer-events: none;
    position: relative;
}

.chat-locked::before {
    content: "🔒 Chat Locked";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 255, 255, 0.9);
    padding: 1rem 2rem;
    border-radius: 8px;
    font-weight: bold;
    z-index: 10;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1000;
    animation: slideIn 0.3s ease;
}

.toast-success { background: #28a745; }
.toast-error { background: #dc3545; }
.toast-info { background: #17a2b8; }

.toast-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.toast-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
}

@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = chatSecurityCSS;
document.head.appendChild(style);
