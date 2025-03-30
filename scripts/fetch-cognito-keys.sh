#!/bin/bash

# Get these values from terraform output
AWS_REGION="${AWS_REGION:-ap-southeast-1}"
USER_POOL_ID="${AWS_COGNITO_USER_POOL_ID}"

# Fetch the JWKS from Cognito
JWKS_URL="https://cognito-idp.${AWS_REGION}.amazonaws.com/${USER_POOL_ID}/.well-known/jwks.json"
echo "Fetching JWKS from: ${JWKS_URL}"

curl -s "${JWKS_URL}" > ./kong/config/jwks.json

echo "JWKS saved to ./kong/config/jwks.json"