# 🦘 Bookaroo

Bookaroo is an advanced platform designed to enhance the event discovery and booking experience.

We help event creators connect with the right audience through intelligent matching, while offering a smooth experience for ticketing, bookings, and refunds.

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Technical Overview Diagram](#technical-overview-diagram)
3. [Frameworks and Databases Utilised](#frameworks-and-databases-utilised)
4. [Setting up a New Microservice](#setting-up-a-new-microservice)
5. [Contributing](#contributing)
6. [Monitoring with Prometheus and Grafana](#monitoring-with-prometheus-and-grafana)

## Quick Start

### Prerequisites

1. Docker ([Windows](https://docs.docker.com/desktop/install/windows-install/) | [MacOS](https://docs.docker.com/desktop/install/mac-install/))

### Local Development Setup

1. Setp up `.env` file

   1. In the root directory of the project, you'll find a file named `.example.env`
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

## Technical Overview Diagram

<img width="1508" alt="Technical Overview Diagram" src="/assets/bookaroo_technical_diagram.png">

## Frameworks and Databases Utilised

<p align="center"><strong>Programming Languages</strong></p>
<p align="center">
<a href="https://www.python.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png" alt="Python" height="40"/></a>&nbsp;&nbsp;
<a href="https://learn.microsoft.com/en-us/dotnet/csharp/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/C_Sharp_wordmark.svg/1200px-C_Sharp_wordmark.svg.png" alt="C#" height="40"/></a>&nbsp;&nbsp;
<a href="https://www.java.com/"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/3/30/Java_programming_language_logo.svg/1200px-Java_programming_language_logo.svg.png" alt="Java" height="40"/></a>&nbsp;&nbsp;
<a href="https://www.typescriptlang.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Typescript_logo_2020.svg/1200px-Typescript_logo_2020.svg.png" alt="TypeScript" height="40"/></a>&nbsp;&nbsp;
<br>
<i>Python · C# · Java · TypeScript</i>
</p>
<br>

<p align="center"><strong>Frameworks</strong></p>
<p align="center">
<a href="https://spring.io/"><img src="https://4.bp.blogspot.com/-ou-a_Aa1t7A/W6IhNc3Q0gI/AAAAAAAAD6Y/pwh44arKiuM_NBqB1H7Pz4-7QhUxAgZkACLcBGAs/s1600/spring-boot-logo.png" alt="SpringBoot" height="40"/></a>&nbsp;&nbsp;
<a href="https://fastapi.tiangolo.com/"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI" height="40"/></a>&nbsp;&nbsp;
<a href="https://flask.palletsprojects.com/"><img src="https://flask.palletsprojects.com/en/3.0.x/_static/flask-vertical.png" alt="Flask" height="40"/></a>&nbsp;&nbsp;
<a href="https://nextjs.org/"><img src="https://assets.vercel.com/image/upload/v1662130559/nextjs/Icon_light_background.png" alt="Next.js" height="40"/></a>&nbsp;&nbsp;
<br>
<i>Spring Boot · FastAPI · Flask · Next.js</i>
</p>
<br>

<p align="center"><strong>API Gateway</strong></p>
<p align="center">
<a href="https://konghq.com/"><img src="https://konghq.com/wp-content/uploads/2018/08/kong-combination-mark-color-256px.png" alt="Kong API Gateway" width="88"/></a>
</p>
<br>

<p align="center"><strong>Monitoring & Observability</strong></p>
<p align="center">
<a href="https://grafana.com/"><img src="https://raw.githubusercontent.com/grafana/scenes/main/docusaurus/website/static/img/logo.svg" alt="Grafana" height="40"/></a>&nbsp;&nbsp;
<a href="https://prometheus.io/"><img src="https://raw.githubusercontent.com/prometheus/docs/ca2961b495c3e2a1e4586899c26de692fa5a28e7/static/prometheus_logo_orange_circle.svg" alt="Prometheus" height="40"/></a>
<br>
<i>Metrics Collection · Real-time Monitoring · Custom Dashboards</i>
</p>
<br>

<p align="center"><strong>Authentication & Authorization</strong></p>
<p align="center">
<a href="https://aws.amazon.com/cognito/"><img src="https://logodix.com/logo/5867.png" alt="AWS Cognito" height="40"/></a>
<br>
<i>User Authentication · JWT Token Management</i>
</p>
<br>

<p align="center"><strong>Storage Solutions</strong></p>  
<p align="center">
<a href="https://www.postgresql.org/"><img src="https://raw.githubusercontent.com/docker-library/docs/01c12653951b2fe592c1f93a13b4e289ada0e3a1/postgres/logo.png" alt="PostgreSQL" height="50"/></a>&nbsp;&nbsp;
<a href="https://aws.amazon.com/s3/"><img src="https://logodix.com/logo/5867.png" alt="S3" height="40"/></a>&nbsp;&nbsp;
<br>
<i>postgreSQL · S3</i>
</p>
<br>

<p align="center"><strong>Message Brokers</strong></p>
<p align="center">
<a href="https://www.rabbitmq.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/RabbitMQ_logo.svg/2560px-RabbitMQ_logo.svg.png" alt="RabbitMQ" width="100"/></a>
<br>
<i>rabbitMQ</i>
</p>
<br>

<p align="center"><strong>Inter-service Communications</strong></p>
<p align="center">
<a href="https://restfulapi.net/"><img src="https://keenethics.com/wp-content/uploads/2022/01/rest-api-1.svg" alt="REST API" height="40"/></a>
</p>

<p align="center"><strong>Other Technologies</strong></p>
<p align="center">
<a href="https://stripe.com/en-gb-sg"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Stripe_Logo%2C_revised_2016.svg/1280px-Stripe_Logo%2C_revised_2016.svg.png" alt="Stripe Payment API" height="40"/></a>&nbsp;&nbsp;
<a href="https://www.docker.com/"><img src="https://www.docker.com/wp-content/uploads/2022/03/horizontal-logo-monochromatic-white.png" alt="Docker" height="30"/></a>&nbsp;&nbsp;
<a href="https://www.terraform.io/"><img src="https://logodix.com/logo/1686023.png" alt="Terraform" height="50"/></a>&nbsp;&nbsp;
<a href="https://www.terraform.io/"><img src="https://logodix.com/logo/5867.png" alt="AWS ECR" height="50"/></a>&nbsp;&nbsp;
</p>
<p align="center">
<i>Docker Compose · Docker Hub · Terraform · AWS ECR</i>
</p>
<br>

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
