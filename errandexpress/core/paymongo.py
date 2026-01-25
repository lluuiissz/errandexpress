"""
PayMongo Integration for ErrandExpress
Handles payment processing for the ₱2 system fee and task payments
LIVE PRODUCTION KEYS INTEGRATED
"""

import requests
import base64
import json
import os
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PayMongoClient:
    """PayMongo API client for handling payments"""
    
    def __init__(self):
        self.secret_key = settings.PAYMONGO_SECRET_KEY
        self.public_key = settings.PAYMONGO_PUBLIC_KEY
        self.base_url = "https://api.paymongo.com/v1"
        
        # Create authorization header
        auth_string = f"{self.secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    def create_payment_intent(self, amount, currency="PHP", description="ErrandExpress Payment"):
        """
        Create a payment intent for the given amount
        Amount should be in centavos (₱1 = 100 centavos)
        """
        try:
            # Convert amount to centavos (handle Decimal types)
            amount_centavos = int(float(amount) * 100)
            
            payload = {
                "data": {
                    "attributes": {
                        "amount": amount_centavos,
                        "currency": currency,
                        "description": description,
                        "statement_descriptor": "ErrandExpress",
                        "payment_method_allowed": [
                            "card",
                            "paymaya",
                            "gcash"
                        ]
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/payment_intents",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PayMongo payment intent creation failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"PayMongo payment intent error: {str(e)}")
            return None
    
    def attach_payment_method(self, payment_intent_id, payment_method_id):
        """Attach a payment method to a payment intent"""
        try:
            payload = {
                "data": {
                    "attributes": {
                        "payment_method": payment_method_id
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/payment_intents/{payment_intent_id}/attach",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PayMongo payment method attachment failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"PayMongo payment method attachment error: {str(e)}")
            return None
    
    def create_source(self, amount, source_type="gcash", currency="PHP", success_url=None, failed_url=None, description="ErrandExpress Payment"):
        """Create a payment source (for GCash, PayMaya, etc.)"""
        try:
            # Convert amount to centavos (handle Decimal types)
            amount_centavos = int(float(amount) * 100)
            
            # Validate amount
            if amount_centavos <= 0:
                logger.error(f"Invalid amount: {amount_centavos} centavos")
                return None
            
            # Use provided URLs or fall back to default
            if not success_url:
                success_url = f"https://{settings.ALLOWED_HOSTS[0]}/payment/success/"
            if not failed_url:
                failed_url = f"https://{settings.ALLOWED_HOSTS[0]}/payment/failed/"
            
            # Ensure URLs are valid
            if not success_url.startswith('http'):
                logger.error(f"Invalid success URL: {success_url}")
                return None
            if not failed_url.startswith('http'):
                logger.error(f"Invalid failed URL: {failed_url}")
                return None
                
            payload = {
                "data": {
                    "attributes": {
                        "amount": amount_centavos,
                        "currency": currency,
                        "type": source_type,
                        "description": description,
                        "redirect": {
                            "success": success_url,
                            "failed": failed_url
                        }
                    }
                }
            }
            
            logger.info(f"Creating PayMongo source: type={source_type}, amount={amount_centavos} centavos, description={description}")
            
            response = requests.post(
                f"{self.base_url}/sources",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"PayMongo source created successfully")
                return response.json()
            else:
                logger.error(f"PayMongo source creation failed: Status={response.status_code}, Response={response.text}")
                return None
                
        except Exception as e:
            logger.error(f"PayMongo source creation error: {str(e)}")
            return None
    
    def retrieve_payment_intent(self, payment_intent_id):
        """Retrieve payment intent details"""
        try:
            response = requests.get(
                f"{self.base_url}/payment_intents/{payment_intent_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PayMongo payment intent retrieval failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"PayMongo payment intent retrieval error: {str(e)}")
            return None
    
    def create_webhook(self, url, events):
        """Create a webhook for payment events"""
        try:
            payload = {
                "data": {
                    "attributes": {
                        "url": url,
                        "events": events
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/webhooks",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PayMongo webhook creation failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"PayMongo webhook creation error: {str(e)}")
            return None


class ErrandExpressPayments:
    """High-level payment handling for ErrandExpress"""
    
    def __init__(self):
        self.paymongo = PayMongoClient()
        self.system_fee = Decimal('2.00')  # ₱2 system fee
    
    def calculate_total_amount(self, task_price):
        """Calculate total amount including system fee"""
        # Convert to Decimal to handle both float and Decimal inputs
        task_price = Decimal(str(task_price))
        return task_price + self.system_fee
    
    def create_system_fee_payment(self, task, payer):
        """Create payment intent for 10% system fee (Add-on Model)"""
        from .models import SystemCommission
        
        try:
            # Calculate 10% fee dynamically
            system_fee = Decimal(str(task.price)) * Decimal('0.10')
            
            # Create payment intent
            payment_intent = self.paymongo.create_payment_intent(
                amount=system_fee,
                description=f"ErrandExpress System Fee - Task: {task.title}"
            )
            
            if payment_intent:
                # Create system commission record
                commission = SystemCommission.objects.create(
                    task=task,
                    payer=payer,
                    amount=system_fee,
                    method='online',
                    paymongo_payment_id=payment_intent['data']['id']
                )
                
                return {
                    'success': True,
                    'payment_intent': payment_intent,
                    'commission': commission
                }
            else:
                return {'success': False, 'error': 'Failed to create payment intent'}
                
        except Exception as e:
            logger.error(f"System fee payment creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_task_payment(self, task, payer, receiver):
        """Create payment intent for task payment"""
        from .models import Payment
        
        try:
            # Calculate Total Amount (Add-On Model)
            # Poster pays Task Price + 10% Service Fee
            task_price = float(task.price)
            service_fee = task_price * 0.10
            total_amount = task_price + service_fee
            
            payment_intent = self.paymongo.create_payment_intent(
                amount=total_amount,
                description=f"Task Payment: {task.title} (incl. Service Fee)"
            )
            
            if payment_intent:
                # Create payment record
                # We store the TOTAL amount paid (e.g. 110)
                # The model's save() method will split it back into 100 (net) and 10 (commission)
                payment = Payment.objects.create(
                    task=task,
                    payer=payer,
                    receiver=receiver,
                    amount=total_amount,
                    method='paymongo',
                    paymongo_payment_id=payment_intent['data']['id']
                )
                
                return {
                    'success': True,
                    'payment_intent': payment_intent,
                    'payment': payment
                }
            else:
                return {'success': False, 'error': 'Failed to create payment intent'}
                
        except Exception as e:
            logger.error(f"Task payment creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_gcash_payment(self, amount, description="ErrandExpress Payment", success_url=None, failed_url=None):
        """Create GCash payment source
        
        Args:
            amount: The payment amount
            description: Payment description
            success_url: Custom success redirect URL (optional)
            failed_url: Custom failed redirect URL (optional)
        """
        try:
            source = self.paymongo.create_source(
                amount=amount,
                source_type="gcash",
                success_url=success_url,
                failed_url=failed_url
            )
            
            if source:
                return {
                    'success': True,
                    'checkout_url': source['data']['attributes']['redirect']['checkout_url'],
                    'source_id': source['data']['id']
                }
            else:
                return {'success': False, 'error': 'Failed to create GCash payment'}
                
        except Exception as e:
            logger.error(f"GCash payment error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_card_payment(self, amount, description="ErrandExpress Payment", success_url=None, failed_url=None):
        """Create card payment source
        
        Args:
            amount: The payment amount
            description: Payment description
            success_url: Custom success redirect URL (optional)
            failed_url: Custom failed redirect URL (optional)
        """
        try:
            source = self.paymongo.create_source(
                amount=amount,
                source_type="card",
                success_url=success_url,
                failed_url=failed_url
            )
            
            if source:
                return {
                    'success': True,
                    'checkout_url': source['data']['attributes']['redirect']['checkout_url'],
                    'source_id': source['data']['id']
                }
            else:
                return {'success': False, 'error': 'Failed to create card payment'}
                
        except Exception as e:
            logger.error(f"Card payment error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, payment_intent_id):
        """Verify payment status"""
        try:
            payment_intent = self.paymongo.retrieve_payment_intent(payment_intent_id)
            
            if payment_intent:
                status = payment_intent['data']['attributes']['status']
                return {
                    'success': True,
                    'status': status,
                    'payment_intent': payment_intent
                }
            else:
                return {'success': False, 'error': 'Payment intent not found'}
                
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return {'success': False, 'error': str(e)}


# Utility functions
def format_amount_for_display(amount):
    """Format amount for display (₱X.XX)"""
    return f"₱{amount:,.2f}"


def format_amount_for_paymongo(amount):
    """Convert amount to centavos for PayMongo API"""
    return int(float(amount) * 100)


def get_payment_method_display_name(method):
    """Get display name for payment method"""
    method_names = {
        'card': 'Credit/Debit Card',
        'gcash': 'GCash',
        'paymaya': 'PayMaya',
        'paymongo': 'Online Payment',
        'cod': 'Cash on Delivery'
    }
    return method_names.get(method, method.title())
