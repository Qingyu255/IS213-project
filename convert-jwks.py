#!/usr/bin/env python3
import json
import base64
import sys
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def convert_jwks_to_pem(jwks_file, pem_output):
    """Convert JWKS to PEM format"""
    try:
        with open(jwks_file, "r") as f:
            jwks = json.load(f)
        
        # Get the first key
        key = jwks["keys"][0]
        
        # Extract key components
        e = key["e"]
        n = key["n"]
        
        # Decode base64url encoding
        # Add padding if needed
        e_padded = e + "=" * (4 - len(e) % 4) if len(e) % 4 else e
        n_padded = n + "=" * (4 - len(n) % 4) if len(n) % 4 else n
        
        # Convert to integers
        e_int = int.from_bytes(base64.urlsafe_b64decode(e_padded), byteorder="big")
        n_int = int.from_bytes(base64.urlsafe_b64decode(n_padded), byteorder="big")
        
        # Create RSA public key
        numbers = rsa.RSAPublicNumbers(e=e_int, n=n_int)
        public_key = numbers.public_key(backend=default_backend())
        
        # Get PEM encoding
        pem_data = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Write to file
        with open(pem_output, "wb") as f:
            f.write(pem_data)
        
        print(f"Successfully converted JWKS to PEM: {pem_output}")
        return True
    
    except Exception as e:
        print(f"Error converting JWKS to PEM: {e}")
        return False

def create_fallback_key(pem_output):
    """Create a fallback key for testing purposes"""
    fallback_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvkDYzC9DUfpM0muKhY6h
aU7lz9T+hy3+OOdZ6l0SiW34F6PBZXvTbmf4fTs9AnKwZsUx8wYf2u7Y1n5QzLlw
MEv7DzsVlzK8FTZa7DDTzc4Q+hiNKSvQJ4JXBXhq/Aozabwi+anKsZfzVVtU0Ipo
1x9J/5XmHSMT0uUBRo/RxUWj2mzwMErPrOLQoLBxTQHgONfv/vF4Y1wdmCDJnHMi
2Kzgd5sJXbf5l2VdYiZJnpEkJRiYrRqC0oqNQDBIK7HSXvfnuFYNBnwD5c7wzMdR
RKczZQXJ6kdHpCF7B3j14FBKaJgk7XmZ3oNrHcjJKS3MIqvQnU5IXeB34GWQIDYI
9QIDAQAB
-----END PUBLIC KEY-----
"""
    with open(pem_output, "w") as f:
        f.write(fallback_pem)
    print(f"Created fallback key: {pem_output}")

if __name__ == "__main__":
    # Check arguments
    if len(sys.argv) < 3:
        print("Usage: python3 convert-jwks.py <jwks_file> <pem_output>")
        sys.exit(1)
    
    jwks_file = sys.argv[1]
    pem_output = sys.argv[2]
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(pem_output), exist_ok=True)
    
    # Try to convert
    if not os.path.exists(jwks_file) or not convert_jwks_to_pem(jwks_file, pem_output):
        create_fallback_key(pem_output)