#!/bin/bash

# Wait for Kong to be ready
echo "Waiting for Kong to be ready..."
until curl -s http://kong:8001/status > /dev/null; do
  sleep 5
  echo "Still waiting..."
done
echo "Kong is ready!"

# Create services
curl -s -X POST http://kong:8001/services -d name=auth-public -d url=http://user-management-service:8080

# Create routes
curl -s -X POST http://kong:8001/services/auth-public/routes -d 'paths[]=/api/users/create' -d 'strip_path=false'

# Add JWT plugin to all services EXCEPT auth-public
# This configuration skips the JWT plugin for auth-public
curl -s -X POST http://kong:8001/plugins -d name=jwt -d 'config.secret_is_base64=false' -d 'config.claims_to_verify=exp' -d 'config.run_on_preflight=true'

# Add CORS plugin globally
curl -s -X POST http://kong:8001/plugins -d name=cors -d 'config.origins=http://localhost:3000' -d 'config.methods=GET,POST,PUT,DELETE,OPTIONS,PATCH' -d 'config.headers=Accept,Accept-Version,Content-Length,Content-MD5,Content-Type,Date,X-Auth-Token,Authorization' -d 'config.exposed_headers=X-Auth-Token' -d 'config.credentials=true' -d 'config.max_age=3600' -d 'config.preflight_continue=false'

echo "Kong configuration completed!"