import requests
import sys
import os
from dotenv import load_dotenv
import boto3
import json

# Load environment variables
load_dotenv()

def get_cognito_token(username, password):
    """Get a JWT token from AWS Cognito"""
    client = boto3.client('cognito-idp',
                        region_name=os.getenv('AWS_REGION'),
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    try:
        response = client.initiate_auth(
            ClientId=os.getenv('AWS_COGNITO_APP_CLIENT_ID'),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # Get the ID token
        id_token = response['AuthenticationResult']['IdToken']
        return id_token
    except Exception as e:
        print(f"Error getting Cognito token: {e}")
        return None

def test_protected_route(token):
    """Test a protected route with the JWT token"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Test routes through Kong gateway
    kong_url = "http://localhost:8100"
    
    # Test User Management API (protected)
    print("\nTesting User Management API (protected)...")
    response = requests.get(f'{kong_url}/api/users', headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test Tickets API (protected)
    print("\nTesting Tickets API (protected)...")
    response = requests.get(f'{kong_url}/api/v1/tickets/1', headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test Events Detail API (protected)
    print("\nTesting Events Detail API (protected)...")
    response = requests.get(f'{kong_url}/api/v1/events/1', headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    return any(r.status_code == 200 for r in [response])

def test_public_route():
    """Test a public route without JWT token"""
    # Test routes through Kong gateway
    kong_url = "http://localhost:8100"
    
    # Test Events Listing API (public)
    print("\nTesting Events Listing API (public)...")
    response = requests.get(f'{kong_url}/api/v1/events')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test User Creation API (public)
    print("\nTesting User Creation API (public)...")
    test_user = {
        "email": "test@example.com",
        "password": "Test1234!",
        "firstName": "Test",
        "lastName": "User"
    }
    # Just testing access, not actually creating user
    response = requests.options(f'{kong_url}/api/users/create')
    print(f"Status Code: {response.status_code}")
    
    return response.status_code in [200, 204]

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_cognito_jwt.py <username> <password>")
        return
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    # Get a token from Cognito
    token = get_cognito_token(username, password)
    
    if not token:
        print("Failed to get token")
        return
    
    print("Token obtained successfully")
    
    # Test public route
    print("\nTesting public routes...")
    if test_public_route():
        print("Public route test passed!")
    else:
        print("Public route test failed!")
    
    # Test protected route
    print("\nTesting protected routes...")
    if test_protected_route(token):
        print("Protected route test passed!")
    else:
        print("Protected route test failed!")

if __name__ == "__main__":
    main()