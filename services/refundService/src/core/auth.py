from fastapi import HTTPException, Security, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import requests
import time
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load environment variables
load_dotenv()

# Cognito configuration from environment variables
REGION = os.getenv("AWS_COGNITO_REGION", "ap-southeast-1")
USER_POOL_ID = os.getenv("AWS_COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("AWS_COGNITO_APP_CLIENT_ID")

logger.debug(f"Auth Config - Region: {REGION}, Pool: {USER_POOL_ID}, Client: {CLIENT_ID}")

if not all([USER_POOL_ID, CLIENT_ID]):
    raise ValueError("Missing required environment variables: AWS_COGNITO_USER_POOL_ID, AWS_COGNITO_APP_CLIENT_ID")

COGNITO_DOMAIN = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"

# JWT configuration
ALGORITHMS = ["RS256"]
security = HTTPBearer()

# Cache for JWKS
_jwks_cache: Dict = {}
_jwks_cache_timestamp = 0
JWKS_CACHE_DURATION = 3600  # Cache JWKS for 1 hour

def get_jwks() -> dict:
    """Fetch and cache the JWKS from Cognito"""
    global _jwks_cache, _jwks_cache_timestamp
    current_time = time.time()
    
    # Return cached JWKS if still valid
    if _jwks_cache and (current_time - _jwks_cache_timestamp) < JWKS_CACHE_DURATION:
        return _jwks_cache
    
    # Fetch new JWKS
    jwks_url = f"{COGNITO_DOMAIN}/.well-known/jwks.json"
    logger.debug(f"Fetching JWKS from: {jwks_url}")
    response = requests.get(jwks_url)
    if response.status_code != 200:
        logger.error(f"Failed to fetch JWKS: {response.status_code} - {response.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
    
    _jwks_cache = response.json()
    _jwks_cache_timestamp = current_time
    logger.debug("JWKS fetched and cached successfully")
    return _jwks_cache

def get_key(kid: str) -> Optional[str]:
    """Get the public key from JWKS matching the key ID"""
    import base64
    import struct
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    jwks = get_jwks()
    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            logger.debug(f"Found matching key for kid: {kid}")
            
            # Get the key components
            e = base64.urlsafe_b64decode(key_data['e'] + '===')
            n = base64.urlsafe_b64decode(key_data['n'] + '===')
            
            # Convert the exponent
            e_val = int.from_bytes(e, 'big')
            
            # Convert the modulus
            n_val = int.from_bytes(n, 'big')
            
            # Create the public key
            pub_numbers = RSAPublicNumbers(e_val, n_val)
            pub_key = pub_numbers.public_key(backend=default_backend())
            
            # Get the PEM format of the public key
            pem = pub_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return pem.decode('utf-8')
            
    logger.warning(f"No matching key found for kid: {kid}")
    return None

def validate_token(authorization: str = Header(None)) -> dict:
    try:
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract the token - handle both with and without Bearer prefix
        token = authorization.split(" ")[-1]  # Take the last part after any spaces

        # First decode without verification to get the header and check format
        try:
            unverified_claims = jwt.decode(token, 'dummy_key', options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False
            })
            logger.debug("=== Unverified Token Claims ===")
            logger.debug(f"Token use: {unverified_claims.get('token_use')}")
            logger.debug(f"Client ID: {unverified_claims.get('client_id')}")
            logger.debug(f"Audience: {unverified_claims.get('aud')}")
            logger.debug(f"Subject (sub): {unverified_claims.get('sub')}")
            logger.debug(f"custom:id: {unverified_claims.get('custom:id')}")
            logger.debug(f"Username: {unverified_claims.get('username') or unverified_claims.get('cognito:username')}")
            
            # Determine token type and expected audience
            token_use = unverified_claims.get('token_use')
            token_aud = unverified_claims.get('aud')
            client_id = unverified_claims.get('client_id')
            logger.debug("=== Token Validation Config ===")
            logger.debug(f"Token type: {token_use}")
            logger.debug(f"Token audience: {token_aud}")
            logger.debug(f"Client ID: {client_id}")
            logger.debug(f"Expected Client ID: {CLIENT_ID}")
            
            # For access tokens, verify against client_id
            # For ID tokens, verify against aud
            if token_use == 'access':
                if client_id != CLIENT_ID:
                    logger.error(f"Invalid client_id. Expected {CLIENT_ID}, got {client_id}")
                    raise HTTPException(status_code=401, detail="Invalid client_id")
                expected_audience = None  # Don't verify audience for access tokens
                verify_aud = False
                logger.debug("Using access token validation rules")
            else:
                expected_audience = CLIENT_ID
                verify_aud = True
                logger.debug("Using ID token validation rules")
            
            logger.debug(f"Expected audience: {expected_audience}")
            logger.debug(f"Verify audience: {verify_aud}")
            
        except Exception as e:
            logger.error(f"Error decoding unverified claims: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid token format: {str(e)}")

        # Get the signing key
        try:
            unverified_header = jwt.get_unverified_header(token)
            logger.debug(f"Token header: {unverified_header}")
            public_key = get_key(unverified_header.get("kid"))
            if not public_key:
                logger.error("Invalid token signing key")
                logger.debug(f"Available keys in JWKS: {get_jwks()}")
                raise HTTPException(status_code=401, detail="Invalid token signing key")
            logger.debug("Found public key")
        except Exception as e:
            logger.error(f"Error getting signing key: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Error validating token signature: {str(e)}")
        
        # Verify and decode the token
        logger.debug(f"Verifying token with issuer: {COGNITO_DOMAIN}")
        
        try:
            claims = jwt.decode(
                token,
                public_key,
                algorithms=ALGORITHMS,
                audience=expected_audience,
                issuer=COGNITO_DOMAIN,
                options={
                    "verify_aud": verify_aud,
                    "verify_exp": True
                }
            )
            logger.debug("Token successfully decoded and verified")
            logger.debug("=== Verified Token Claims ===")
            logger.debug(f"Token use: {claims.get('token_use')}")
            logger.debug(f"Subject (sub): {claims.get('sub')}")
            logger.debug(f"custom:id: {claims.get('custom:id')}")
            logger.debug(f"Username: {claims.get('username') or claims.get('cognito:username')}")
            return claims
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    except HTTPException:
        raise
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        logger.debug(f"Full error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Dependency to get the current user ID from the token
async def get_current_user_id(claims: dict = Depends(validate_token)) -> str:
    """Extract the user ID from the validated token claims"""
    logger.debug("=== Getting user ID from claims ===")
    logger.debug(f"Token type: {claims.get('token_use', 'unknown')}")
    
    # Log all available claims for debugging
    logger.debug("Available claims:")
    for key, value in claims.items():
        logger.debug(f"  {key}: {value}")
    
    # Only use custom:id as the user ID
    user_id = claims.get("custom:id") or claims.get("sub")
    logger.debug(f"Extracted custom:id: {user_id}")
    
    # Extract username and sub for better error messages
    username = (
        claims.get("username") or 
        claims.get("cognito:username") or 
        claims.get("preferred_username")
    )
    sub = claims.get("sub")
    logger.debug(f"Extracted username: {username}")
    logger.debug(f"Extracted sub: {sub}")
    
    if not user_id:
        logger.error("No custom:id or sub found in token claims")
        error_msg = "No custom:id or sub found in token"
        if username:
            error_msg += f" for user {username}"
        if sub:
            error_msg += f" (sub: {sub})"
        logger.error(error_msg)
        logger.error("Available claims for debugging:")
        for key, value in claims.items():
            logger.error(f"  {key}: {value}")
        raise HTTPException(status_code=401, detail=error_msg)
    
    logger.debug(f"Using user ID (custom:id or sub): {user_id}")
    return user_id

# New dependency to get the current username from the token
async def get_current_username(claims: dict = Depends(validate_token)) -> str:
    """Extract the username from the validated token claims"""
    logger.debug("Getting username from claims")
    
    # Try different possible claim names for the username
    username = (
        claims.get("username") or 
        claims.get("cognito:username") or 
        claims.get("preferred_username")
    )
    
    if not username:
        logger.error("No username found in token claims")
        # Try to get user ID for error message
        user_id = claims.get("sub") or claims.get("custom:id")
        if user_id:
            logger.error(f"No username found for user ID {user_id}")
            raise HTTPException(status_code=401, detail=f"No username found for user ID {user_id}")
        else:
            raise HTTPException(status_code=401, detail="No username found in token")
    
    logger.debug(f"Using username: {username}")
    
    # Log the exact username for debugging
    logger.info(f"Extracted username from token: '{username}'")
    
    return username 