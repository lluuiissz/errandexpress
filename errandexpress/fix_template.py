
import os

content = r"""{% extends 'base_complete.html' %}

{% block title %}Pay Commission - ErrandExpress{% endblock %}

{% block content %}
<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-12 px-4">
    <div class="max-w-2xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <i data-lucide="unlock" class="w-8 h-8 text-blue-600"></i>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Unlock Chat</h1>
            <p class="text-lg text-gray-600">Pay commission to start messaging</p>
        </div>

        <!-- Payment Card -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-6">
            <!-- Task Info -->
            <div class="mb-6 pb-6 border-b">
                <h2 class="text-xl font-bold text-gray-900 mb-4">Task Details</h2>
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Task:</span>
                        <span class="font-bold text-gray-900">{{ task.title }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Task Doer:</span>
                        <span class="font-bold text-gray-900">{{ doer.fullname }}</span>
                    </div>
                </div>
            </div>

            <!-- Payment Breakdown -->
            <div class="mb-6 pb-6 border-b">
                <h2 class="text-xl font-bold text-gray-900 mb-4">Payment Breakdown</h2>
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Total Task Amount:</span>
                        <span class="font-bold text-gray-900">₱{{ task.price }}</span>
                    </div>
                    <div class="flex justify-between items-center text-blue-600">
                        <span class="flex items-center gap-1">
                            <i data-lucide="shield-check" class="w-4 h-4"></i>
                            Commission (10%) - Pay Now:
                        </span>
                        <span class="text-2xl font-bold">₱{{ commission_amount }}</span>
                    </div>
                    <div class="flex justify-between items-center text-green-600">
                        <span class="flex items-center gap-1">
                            <i data-lucide="user-check" class="w-4 h-4"></i>
                            Pay to Doer Later:
                        </span>
                        <span class="font-bold">₱{{ doer_payment_amount }}</span>
                    </div>
                </div>
            </div>

            <!-- Info Box -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div class="flex gap-3">
                    <i data-lucide="info" class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5"></i>
                    <div>
                        <p class="text-sm text-blue-900">
                            <strong>Why pay commission?</strong><br>
                            This secures the platform and prevents bypass. After paying, you can chat unlimited with the
                            doer. When the task is completed, you'll pay ₱{{ doer_payment_amount }} directly to the
                            doer.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Payment Form -->
            <form method="POST" class="space-y-4">
                {% csrf_token %}

                <!-- Full Name -->
                <div>
                    <label class="block text-sm font-bold text-gray-900 mb-2">Full Name *</label>
                    <input type="text" name="fullname" value="{{ fullname }}" required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        placeholder="Your full name">
                </div>

                <!-- Phone -->
                <div>
                    <label class="block text-sm font-bold text-gray-900 mb-2">Phone Number *</label>
                    <input type="tel" name="phone" value="{{ phone }}" required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        placeholder="09XXXXXXXXX">
                </div>

                <!-- Email -->
                <div>
                    <label class="block text-sm font-bold text-gray-900 mb-2">Email Address *</label>
                    <input type="email" name="email" value="{{ email }}" required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        placeholder="your@email.com">
                </div>

                <!-- Payment Methods -->
                <div class="pt-4">
                    <h3 class="text-lg font-bold text-gray-900 mb-3">Select Payment Method</h3>

                    {% for method in payment_methods %}
                    <label
                        class="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 transition mb-3">
                        <input type="radio" name="payment_method" value="{{ method.value }}" {% if forloop.first %}checked{% endif %} class="w-4 h-4 text-blue-600">
                        <div class="ml-4 flex-grow">
                            <div class="font-bold text-gray-900">{{ method.name }}</div>
                            <div class="text-sm text-gray-600">
                                {% if method.value == 'gcash' %}
                                Pay via GCash - Fast and secure
                                {% elif method.value == 'card' %}
                                Pay via Credit/Debit Card
                                {% endif %}
                            </div>
                        </div>
                        <span class="text-2xl">{{ method.icon }}</span>
                    </label>
                    {% endfor %}
                </div>

                <!-- Submit Button -->
                <button type="submit"
                    class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2 mt-6">
                    <i data-lucide="unlock" class="w-5 h-5"></i>
                    Pay ₱{{ commission_amount }} - Unlock Chat
                </button>
            </form>
        </div>

        <!-- Back Link -->
        <div class="text-center">
            <a href="{% url 'task_detail' task.id %}"
                class="text-blue-600 hover:text-blue-800 font-medium flex items-center justify-center gap-2">
                <i data-lucide="arrow-left" class="w-4 h-4"></i>
                Back to Task
            </a>
        </div>
    </div>
</div>

<script>
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
</script>
{% endblock %}
"""

path = r'core/templates/payments/commission_payment.html'
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Successfully wrote to {path}")
