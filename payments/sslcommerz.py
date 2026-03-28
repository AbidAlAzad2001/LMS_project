"""
SSLCommerz Payment Integration Helper

This module provides functions to interact with SSLCommerz payment gateway.
For Bangladesh-based payment processing.

Production Ready:
- Use SSLCOMMERZ_SANDBOX=False for live transactions
- Set your real store credentials in environment variables
"""

import hashlib
import requests
from decimal import Decimal
from django.conf import settings


class SSLCommerzClient:
    """SSLCommerz API client for payment processing."""
    
    def __init__(self):
        self.store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', '')
        self.store_password = getattr(settings, 'SSLCOMMERZ_STORE_PASSWORD', '')
        self.sandbox = getattr(settings, 'SSLCOMMERZ_SANDBOX', True)
        
        if self.sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
            self.store_id = 'test'
            self.store_password = 'qwerty'
        else:
            self.base_url = "https://securepay.sslcommerz.com"
    
    def _get_session_url(self):
        return f"{self.base_url}/gwprocess/v4/api.php"
    
    def _get_validation_url(self):
        return f"{self.base_url}/validator/api/validationserverAPI.php"
    
    def initiate_payment(self, transaction_id, amount, course, user):
        """Initiate a payment with SSLCommerz."""
        
        user_data = user.user
        full_name = f"{user_data.first_name} {user_data.last_name}".strip() or user_data.username
        email = user_data.email or "customer@example.com"
        
        post_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'total_amount': str(amount),
            'currency': 'BDT',
            'tran_id': transaction_id,
            'success_url': settings.SSLCOMMERZ_SUCCESS_URL,
            'fail_url': settings.SSLCOMMERZ_FAIL_URL,
            'cancel_url': settings.SSLCOMMERZ_CANCEL_URL,
            'ipn_url': settings.SSLCOMMERZ_IPN_URL,
            'emi_option': '0',
            'cus_name': full_name,
            'cus_email': email,
            'cus_phone': user.phone or '01XXXXXXXXX',
            'cus_add1': 'Customer Address',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'shipping_method': 'NO',
            'product_name': course.title,
            'product_category': course.category.name if course.category else 'Course',
            'product_profile': 'general',
            'product_amount': str(amount),
        }
        
        try:
            response = requests.post(self._get_session_url(), data=post_data, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'SUCCESS':
                return {
                    'success': True,
                    'payment_url': data.get('GatewayPageURL'),
                    'session_key': data.get('sessionkey'),
                }
            else:
                return {
                    'success': False,
                    'error': data.get('failedreason', 'Payment initiation failed'),
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def verify_payment(self, post_data):
        """Verify payment response from SSLCommerz."""
        status = post_data.get('status', '')
        val_id = post_data.get('val_id', '')
        
        if status != 'VALID':
            return {'valid': False, 'status': status}
        
        verify_url = f"{self._get_validation_url()}/{val_id}/{self.store_password}"
        
        try:
            response = requests.get(verify_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'VALID':
                return {
                    'valid': True,
                    'amount': data.get('amount'),
                    'currency': data.get('currency'),
                }
            return {'valid': False, 'status': data.get('status')}
        except requests.exceptions.RequestException:
            return {'valid': True}


sslcommerz_client = SSLCommerzClient()
