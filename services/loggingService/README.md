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
