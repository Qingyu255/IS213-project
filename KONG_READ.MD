# Kong API Gateway Setup and Restoration Guide


## Kong API Gateway has been integrated into the main docker-compose.yml file
The gateway runs on the following ports:

Proxy: 8100 (was 8000)
Admin API: 8101 (was 8001)
Admin GUI: 8102 (was 8002)



## Restore Configuration Script
The restore-kong.sh script allows you to restore your Kong configuration from exported JSON files.
Prerequisites

jq must be installed (for JSON processing)
Kong API Gateway must be running
Configuration files must be in kong/config/ directory

## How to Use

### Make sure Kong is running:

` docker-compose up -d `

### Run the restoration script:

` chmod +x restore-kong.sh
./restore-kong.sh `

### What the Script Does
The script performs the following operations:

Restores all services from kong/config/kong-services.json
Restores all routes from kong/config/kong-routes.json
Restores all plugins from kong/config/kong-plugins.json

It automatically removes fields like id, created_at, and updated_at which should not be included in POST requests.
Troubleshooting
If you get errors about jq not being found, install it:
`# For Ubuntu/Debian
sudo apt-get install jq `

# For Windows (with Git Bash)
` curl -L -o /usr/bin/jq.exe https://github.com/stedolan/jq/releases/download/jq-1.6/jq-win64.exe
chmod +x /usr/bin/jq.exe`