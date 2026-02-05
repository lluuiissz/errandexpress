import boto3
import os
import sys
from botocore.exceptions import ClientError

# Configuration
# Extracting values from settings.py context
PROJECT_ID = "yrkvxspmazdrfpbwerzm" # Extracted from the endpoint URL
REGION = "ap-southeast-1"
ENDPOINT_URL = f"https://{PROJECT_ID}.storage.supabase.co/storage/v1/s3"

# Try getting keys from environment, or fallback to what might be in settings (though we cant read settings variables directly easily without django setup, we'll try to use the ones likely available)
# In this environment, we rely on the OS env vars being set or the user having them in .env
# For the purpose of this script, we need the secret key. 
# Since I can't see the actual secret key value in the chat (masked), I will assume it's in the environment.
# If not, this script might fail, and I'll have to ask the user to provide it or set it.

ACCESS_KEY = PROJECT_ID # Standard for Supabase S3 with Service Role
SECRET_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SECRET_KEY:
    print("Error: SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY environment variable not set.")
    print("Please set it in your terminal or .env file.")
    # Attempt to read from .env file manually if exists
    try:
        with open('.env', 'r') as f:
            for line in f:
                if 'SUPABASE_SERVICE_ROLE_KEY=' in line:
                    SECRET_KEY = line.split('=')[1].strip().strip("'").strip('"')
                    break
                elif 'SUPABASE_KEY=' in line and not SECRET_KEY:
                    SECRET_KEY = line.split('=')[1].strip().strip("'").strip('"')
    except:
        pass

if not SECRET_KEY:
    print("CRITICAL: Could not find Supabase Secret Key.")
    sys.exit(1)

BUCKET_NAME = "errand-uploads"

def create_bucket():
    print(f"Connecting to Supabase S3 at {ENDPOINT_URL}...")
    print(f"Using Access Key: {ACCESS_KEY}")
    
    s3 = boto3.client(
        's3',
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION
    )

    try:
        print(f"Creating bucket '{BUCKET_NAME}'...")
        s3.create_bucket(Bucket=BUCKET_NAME, ACL='public-read') # Try 'public-read' but Supabase might ignore ACLs
        print(f"Successfully created bucket: {BUCKET_NAME}")
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "BucketAlreadyOwnedByYou":
            print(f"Bucket '{BUCKET_NAME}' already exists and is owned by you.")
            return True
        elif error_code == "403":
             print("Error: 403 Forbidden. This confirms credentials or permissions issue.")
             print("Try checking if the Service Role Key is correct.")
        else:
            print(f"Failed to create bucket: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    success = create_bucket()
    if success:
        print("\nSUCCESS! You can now update your settings.py:")
        print(f'AWS_ACCESS_KEY_ID = "{ACCESS_KEY}"')
        print(f'AWS_STORAGE_BUCKET_NAME = "{BUCKET_NAME}"')
    else:
        print("\nFAILURE. Please try creating the bucket manually in the Supabase Dashboard.")
