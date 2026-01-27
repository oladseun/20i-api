"""
Convert 20i General API Key to Base64 Bearer Token
"""
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Get the general API key from .env
general_api_key = os.getenv('TWENTYI_API_TOKEN', '')

print("20i API Token Encoder")
print("=" * 50)
print(f"Your current token: {general_api_key}")
print(f"Token length: {len(general_api_key)} characters")
print()

# Base64 encode the token
encoded_token = base64.b64encode(general_api_key.encode('utf-8')).decode('utf-8')

print("Base64 Encoded Token:")
print(encoded_token)
print()
print(f"Encoded token length: {len(encoded_token)} characters")
print()
print("=" * 50)
print("INSTRUCTIONS:")
print("=" * 50)
print("1. Copy the encoded token above")
print("2. Open your .env file")
print("3. Replace the TWENTYI_API_TOKEN value with the encoded token")
print()
print("Example:")
print(f"TWENTYI_API_TOKEN={encoded_token}")
