#!/bin/bash

KONG_ADMIN_URL="http://localhost:8101"

echo "Restoring Kong Services..."
cat kong/config/kong-services.json | grep -v "^\s*$" | jq -c '.data[]' | while read service; do
  # Remove fields that shouldn't be in POST requests
  service_clean=$(echo $service | jq 'del(.id, .created_at, .updated_at)')
  name=$(echo $service | jq -r '.name')
  echo "Creating service: $name"
  curl -s -X POST $KONG_ADMIN_URL/services \
    -H "Content-Type: application/json" \
    -d "$service_clean"
  echo ""
done

echo "Restoring Kong Routes..."
cat kong/config/kong-routes.json | grep -v "^\s*$" | jq -c '.data[]' | while read route; do
  # Remove fields that shouldn't be in POST requests
  route_clean=$(echo $route | jq 'del(.id, .created_at, .updated_at)')
  name=$(echo $route | jq -r '.name // "unnamed"')
  echo "Creating route: $name"
  curl -s -X POST $KONG_ADMIN_URL/routes \
    -H "Content-Type: application/json" \
    -d "$route_clean"
  echo ""
done

echo "Restoring Kong Plugins..."
cat kong/config/kong-plugins.json | grep -v "^\s*$" | jq -c '.data[]' | while read plugin; do
  # Remove fields that shouldn't be in POST requests
  plugin_clean=$(echo $plugin | jq 'del(.id, .created_at, .updated_at)')
  name=$(echo $plugin | jq -r '.name')
  echo "Creating plugin: $name"
  curl -s -X POST $KONG_ADMIN_URL/plugins \
    -H "Content-Type: application/json" \
    -d "$plugin_clean"
  echo ""
done

echo "Kong configuration restoration completed!"
