# IS213-project

## Local Development Setup
1. Setp up `.env` file
    1. In the root directory of the project, you’ll find a file named `.example.env`
    2. Create a new `.env` file in the same directory by copying `.example.env`
    3. Populate relevant env variables.

2. Ensure you have **Docker Desktop** installed and opened with your Docker Daemon running.
3. Build the Docker image:
   ```
   docker compose build
   ```
4. Run the application:
   ```
   docker compose up
   ```
   This should spins up the docker containers. Ensure no errors in each container.

## Setting up a new microservice
Refer to [MICROSERVICE_SETUP_GUIDE.md](./MICROSERVICE_SETUP_GUIDE.MD)

## Contributing
Refer to [CONTRIBUTING.md](./CONTRIBUTING.MD)

## Monitoring with Prometheus and Grafana

### Overview
The project includes a comprehensive monitoring setup using Prometheus for metrics collection and Grafana for visualization.

### Features
- Real-time monitoring of all microservices
- Health status checks (UP/DOWN indicators)
- Performance metrics (CPU, memory usage)
- HTTP request rates and latencies
- Error rate tracking

### Accessing Monitoring Tools
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (login: admin/admin)

### Architecture
- Each service exposes metrics either directly or via a dedicated endpoint
- Prometheus scrapes metrics every 15 seconds
- Grafana dashboard provides a unified view of all services

### Supported Services
All microservices in the project are monitored, namely:
- User Management Service
- Ticket Management Service
- Booking Service
- Billing Service
- Refund Service
- Events Service
- Create Event Service
- Logging Service
