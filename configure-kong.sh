#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Use KONG_ADMIN_URL environment variable if set, otherwise use default
KONG_ADMIN_URL=${KONG_ADMIN_URL:-"http://kong:8001"}
echo "Using Kong Admin API at: $KONG_ADMIN_URL"

# Check if Kong is already configured by looking for a specific service
echo "Checking if Kong is already configured..."
CONFIGURED=$(curl -s $KONG_ADMIN_URL/services/user-management-service 2>/dev/null || echo "")
if [[ $CONFIGURED != *"message\":\"Not found"* ]] && [[ $CONFIGURED != "" ]]; then
    echo "Kong appears to be already configured. Skipping configuration."
    exit 0
fi

echo "Kong not configured. Proceeding with configuration..."

# Wait for Kong to be ready
echo "Checking if Kong Admin API is available..."
max_retries=30
retries=0

while [[ $retries -lt $max_retries ]]; do
    if curl -s -o /dev/null -w "%{http_code}" $KONG_ADMIN_URL/status | grep -q "200"; then
        echo "Kong Admin API is available!"
        break
    else
        retries=$((retries+1))
        if [[ $retries -eq $max_retries ]]; then
            echo "Error: Kong Admin API did not become available after $max_retries attempts."
            exit 1
        fi
        echo "Waiting for Kong Admin API to be available... (Attempt $retries/$max_retries)"
        sleep 5
    fi
done

# Service endpoints based on frontend routes
USER_MGMT_URL="http://user-management-service:8080"
EVENTS_URL="http://events-service:8001"
CREATE_EVENTS_URL="http://create-event-service:8070"
BILLING_URL="http://billing-service:5001"
TICKET_MGMT_URL="http://ticket-management-service:8000"
BOOKING_URL="http://booking-service:8002"

# Create services
echo "Creating services..."
curl -s -X POST $KONG_ADMIN_URL/services \
    -d "name=user-management-service" \
    -d "url=$USER_MGMT_URL"

curl -s -X POST $KONG_ADMIN_URL/services \
    -d "name=events-service" \
    -d "url=$EVENTS_URL"

curl -s -X POST $KONG_ADMIN_URL/services \
    -d "name=create-event-service" \
    -d "url=$CREATE_EVENTS_URL"

curl -s -X POST $KONG_ADMIN_URL/services \
    -d "name=billing-service" \
    -d "url=$BILLING_URL"

curl -s -X POST $KONG_ADMIN_URL/services \
    -d "name=ticket-management-service" \
    -d "url=$TICKET_MGMT_URL"

curl -s -X POST $KONG_ADMIN_URL/services \
    -d "name=booking-service" \
    -d "url=$BOOKING_URL"

# Create routes
echo "Creating routes..."

# User Management Routes
curl -s -X POST $KONG_ADMIN_URL/services/user-management-service/routes \
    -d "name=user-creation-route" \
    -d "paths[]=/api/users/create" \
    -d "methods[]=POST" \
    -d "strip_path=false"

curl -s -X POST $KONG_ADMIN_URL/services/user-management-service/routes \
    -d "name=user-management-wildcard-route" \
    -d "paths[]=/api/users" \
    -d "paths[]=/api/users/*" \
    -d "methods[]=GET" \
    -d "methods[]=PUT" \
    -d "methods[]=DELETE" \
    -d "strip_path=false"

# Events Routes
curl -s -X POST $KONG_ADMIN_URL/services/events-service/routes \
    -d "name=events-listings-routes" \
    -d "paths[]=/api/v1/events" \
    -d "methods[]=GET" \
    -d "strip_path=false"

curl -s -X POST $KONG_ADMIN_URL/services/events-service/routes \
    -d "name=events-wildcard-route" \
    -d "paths[]=/api/v1/events/*" \
    -d "methods[]=PUT" \
    -d "methods[]=DELETE" \
    -d "methods[]=POST" \
    -d "strip_path=false"

# Create Event Service Route
curl -s -X POST $KONG_ADMIN_URL/services/create-event-service/routes \
    -d "name=event-creation-route" \
    -d "paths[]=/api/v1/events/create" \
    -d "methods[]=POST" \
    -d "strip_path=false"

# Ticket Management Routes
curl -s -X POST $KONG_ADMIN_URL/services/ticket-management-service/routes \
    -d "name=ticket-management-wildcard-route" \
    -d "paths[]=/api/v1/tickets/*" \
    -d "paths[]=/api/v1/bookings/*" \
    -d "methods[]=GET" \
    -d "methods[]=PUT" \
    -d "methods[]=POST" \
    -d "methods[]=DELETE" \
    -d "strip_path=false"

# Billing Service Routes
curl -s -X POST $KONG_ADMIN_URL/services/billing-service/routes \
    -d "name=billing-service-route" \
    -d "paths[]=/api/billing" \
    -d "paths[]=/api/billing/*" \
    -d "methods[]=GET" \
    -d "methods[]=POST" \
    -d "strip_path=false"

# Booking Service Routes
curl -s -X POST $KONG_ADMIN_URL/services/booking-service/routes \
    -d "name=booking-service-route" \
    -d "paths[]=/api/bookings" \
    -d "paths[]=/api/bookings/*" \
    -d "methods[]=GET" \
    -d "methods[]=POST" \
    -d "strip_path=false"

# Create Cognito Consumer
echo "Creating Cognito consumer..."
curl -s -X POST $KONG_ADMIN_URL/consumers \
    -d "username=cognito"

# Configure JWT plugin for Cognito
echo "Configuring JWT plugin..."
COGNITO_ISSUER="https://cognito-idp.${AWS_REGION}.amazonaws.com/${AWS_COGNITO_USER_POOL_ID}"

# Create temporary public key file for testing
# In production, fetch and convert the real key from Cognito JWKS
mkdir -p kong/config
echo "-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvkDYzC9DUfpM0muKhY6h
aU7lz9T+hy3+OOdZ6l0SiW34F6PBZXvTbmf4fTs9AnKwZsUx8wYf2u7Y1n5QzLlw
MEv7DzsVlzK8FTZa7DDTzc4Q+hiNKSvQJ4JXBXhq/Aozabwi+anKsZfzVVtU0Ipo
1x9J/5XmHSMT0uUBRo/RxUWj2mzwMErPrOLQoLBxTQHgONfv/vF4Y1wdmCDJnHMi
2Kzgd5sJXbf5l2VdYiZJnpEkJRiYrRqC0oqNQDBIK7HSXvfnuFYNBnwD5c7wzMdR
RKczZQXJ6kdHpCF7B3j14FBKaJgk7XmZ3oNrHcjJKS3MIqvQnU5IXeB34GWQIDYI
9QIDAQAB
-----END PUBLIC KEY-----" > kong/config/cognito-public-key.pem

# Add JWT credential for Cognito
curl -s -X POST $KONG_ADMIN_URL/consumers/cognito/jwt \
    -d "key=${COGNITO_ISSUER}" \
    -d "algorithm=RS256" \
    -d "rsa_public_key=@kong/config/cognito-public-key.pem"

# Add global CORS plugin
echo "Adding global CORS plugin..."
curl -s -X POST $KONG_ADMIN_URL/plugins \
    -d "name=cors" \
    -d "config.origins[]=http://localhost:3000" \
    -d "config.methods[]=GET" \
    -d "config.methods[]=POST" \
    -d "config.methods[]=PUT" \
    -d "config.methods[]=DELETE" \
    -d "config.methods[]=OPTIONS" \
    -d "config.headers[]=Content-Type" \
    -d "config.headers[]=Authorization" \
    -d "config.credentials=true" \
    -d "config.preflight_continue=false"

# Define public routes that don't need authentication
PUBLIC_ROUTES=("user-creation-route" "events-listings-routes")

# Get all routes
all_routes=$(curl -s $KONG_ADMIN_URL/routes | jq -c '.data[]')

# Loop through all routes and add JWT plugin to protected routes
echo "$all_routes" | while read -r route_data; do
    route_name=$(echo "$route_data" | jq -r '.name')
    route_id=$(echo "$route_data" | jq -r '.id')
    
    # Check if this route should be public
    is_public=false
    for public_route in "${PUBLIC_ROUTES[@]}"; do
        if [ "$route_name" == "$public_route" ]; then
            is_public=true
            break
        fi
    done
    
    if [ "$is_public" = false ]; then
        echo "Adding JWT plugin to protected route: $route_name"
        curl -s -X POST $KONG_ADMIN_URL/routes/$route_id/plugins \
            -d "name=jwt" \
            -d "config.uri_param_names[]=jwt" \
            -d "config.header_names[]=authorization" \
            -d "config.claims_to_verify[]=exp" \
            -d "config.key_claim_name=iss"
    else
        echo "Skipping JWT plugin for public route: $route_name"
    fi
done

# Create a flag file to indicate configuration is complete
touch /tmp/kong_configured

echo "Kong configuration completed successfully!"