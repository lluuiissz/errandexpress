
import os
import django
from django.conf import settings
import logging

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

# Configure logging to print to console
logging.basicConfig(level=logging.INFO)

from core.paymongo import PayMongoClient

def test_paymongo():
    print("🚀 Initializing PayMongo Client...")
    client = PayMongoClient()
    
    print(f"🔑 Public Key: {client.public_key[:10]}...")
    print(f"🔑 Secret Key: {client.secret_key[:10]}...")
    
    # Test 1: Try to create a small source (e.g. 10 PHP)
    print("\n🧪 Test 1: Creating Card Source for ₱10.00...")
    amount = 10.00
    
    response = client.create_source(
        amount=amount,
        source_type="card",
        description="Debug Test Payment",
        success_url="http://localhost:8000/success",
        failed_url="http://localhost:8000/failed"
    )
    
    if response:
        print("✅ Success! Source created.")
        print(response)
    else:
        print("❌ Failed! (See logs above for details if logger is capturing)")
        # If logger didn't print, let's manually try requests to see raw response
        import requests
        import base64
        
        url = "https://api.paymongo.com/v1/sources"
        auth_string = f"{client.secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "attributes": {
                    "amount": int(amount * 100),
                    "currency": "PHP",
                    "type": "card",
                    "redirect": {
                        "success": "http://localhost:8000/success",
                        "failed": "http://localhost:8000/failed"
                    }
                }
            }
        }
        print("\n🔍 Retrying with manual request to see raw error...")
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {r.status_code}")
        print(f"Response Body: {r.text}")

if __name__ == "__main__":
    test_paymongo()
