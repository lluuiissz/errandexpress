
import os
import django
from django.conf import settings
import logging
import requests
import base64

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'errandexpress.settings')
django.setup()

from core.paymongo import PayMongoClient

def test_paymongo_link():
    print("🚀 Initializing PayMongo Client...")
    client = PayMongoClient()
    
    print("\n🧪 Test 2: Creating Payment Link (Checkout Page)...")
    amount = 100.00 # Minimum might be 100
    
    url = "https://api.paymongo.com/v1/links"
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
                "description": "Debug Link Payment",
                "remarks": "debug_link"
            }
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("✅ Success! Link created.")
        data = response.json()
        print(f"Checkout URL: {data['data']['attributes']['checkout_url']}")
        print(data)
    else:
        print("❌ Failed!")
        print(f"Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_paymongo_link()
