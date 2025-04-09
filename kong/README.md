# Kong API Gateway Setup

This directory contains the configuration for Kong API Gateway, which acts as a central entry point for all microservices in the system.

## Prerequisites

- Docker
- Docker Compose

## Directory Structure

```
kong/
├── declarative/
│   └── kong.yml      # Kong declarative configuration
├── docker-compose.yml # Docker Compose configuration
└── README.md         # This file
```

## Configuration Overview

The Kong setup includes:

1. **Services**: All microservices are registered as services in Kong
2. **Routes**: Each service has its own route with specific paths and methods
3. **Plugins**: Common plugins applied to all services:
   - CORS: For cross-origin resource sharing
   - Rate Limiting: To prevent abuse
   - Prometheus: For metrics collection

## Starting Kong

To start Kong and its dependencies:

```bash
cd kong
docker-compose up -d
```

This will start:
- PostgreSQL database for Kong
- Kong migrations service
- Kong API Gateway

## Accessing Kong

- Kong Admin API: http://localhost:8001
- Kong Proxy: http://localhost:8000
- Kong Metrics: http://localhost:8001/metrics

## Service Endpoints

All services are accessible through Kong at the following paths:

- AI Test Service: http://localhost:8000/ai-test
- Booking Service: http://localhost:8000/booking
- User Management Service: http://localhost:8000/users
- Ticket Management Service: http://localhost:8000/tickets
- Events Service: http://localhost:8000/events
- Billing Service: http://localhost:8000/billing
- Refund Service: http://localhost:8000/refunds
- Logging Service: http://localhost:8000/logs

## Monitoring

Kong provides several monitoring options:

1. **Prometheus Metrics**: Available at http://localhost:8001/metrics
2. **Kong Manager**: Access the admin interface at http://localhost:8001
3. **Logs**: View container logs with `docker-compose logs -f`

## Updating Configuration

To update the Kong configuration:

1. Modify the `declarative/kong.yml` file
2. Restart Kong:
   ```bash
   docker-compose restart kong
   ```

## Security Considerations

1. **Rate Limiting**: Configured to prevent abuse
   - 60 requests per minute
   - 1000 requests per hour

2. **CORS**: Configured to allow requests from:
   - http://localhost:3000 (frontend)

3. **Database**: PostgreSQL credentials are set in the docker-compose file
   - Consider changing these in production

## Troubleshooting

If you encounter issues:

1. Check container status:
   ```bash
   docker-compose ps
   ```

2. View logs:
   ```bash
   docker-compose logs -f kong
   ```

3. Check Kong health:
   ```bash
   curl -i http://localhost:8001/status
   ```

## Additional Resources

- [Kong Documentation](https://docs.konghq.com/)
- [Kong Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/declarative-config/)
- [Kong Docker Installation](https://docs.konghq.com/gateway/latest/install/docker/) 