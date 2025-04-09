# Microservice Project Setup Guide

## **Sample Project Directory Structure**

```plaintext
IS213-project/
│
├── docker-compose.yml               # Docker Compose file to orchestrate all services
├── README.md                        # This guide
├── services/
│   ├── example-spring-service/      # Example Java Spring Boot service
│   │   ├── Dockerfile               # Dockerfile for building and running the  service
│   │   ├── pom.xml                  # Maven configuration file
│   │   └── src/                     # Source code for the Spring Boot application
│   ├── example-python-service/      # Example Python Flask service
│   │   ├── Dockerfile               # Dockerfile for building and running the service
│   │   ├── requirements.txt         # Python dependencies
│   │   └── src/
│   │        └── app.py              # Flask application code
│   └── <your-service>/              # Add your new service here
│
└── shared/
    ├── config/                      # Shared configuration files
    └── libraries/                   # Shared libraries for reuse

```

---

## **Referring to the Example Services**

The `services/example-spring-service` and `services/example-python-service` directories contain fully functional templates for creating microservices. Use these examples as references when creating your own service.

### **Key Features in the Example Services**
1. **Dockerfile**:
   - Shows how to build and run the service using a lightweight image.
   - Includes multi-stage builds for optimized Docker images.
2. **Code Structure**:
   - Provides a clean and modular structure for the application.
3. **Integration with Docker Compose**:
   - Services are pre-configured to work with the `docker-compose.yml` file.

---

## **Setting Up Your Own Service**

### **Step 1: Create a New Service Directory**
1. Copy one of the example service directories (`example-spring-service` or `example-python-service`) into `services/` and rename it:
   ```bash
   cp -r services/example-python-service services/my-new-service
   ```

2. Rename the files or directories as necessary.

---

### **Step 2: Modify the Dockerfile**
Update the `Dockerfile` in your new service directory based on your application's requirements. **Especially** your new port number.

#### Example:
```dockerfile
# Base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 5001

# Run the application
ENTRYPOINT ["python", "app.py"]
```

---

### **Step 3: Update the Application Code**
Modify the application code (`app.py`, `src/main/java/...`, etc.) to reflect your new service's functionality. Ensure the service listens on a unique port that does not conflict with other services.

#### Example for Python Flask:
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to My New Service!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Ensure this port matches the one in your Dockerfile
```

---

### **Step 4: Update `docker-compose.yml`**

1. Open the `docker-compose.yml` file in the project root.
2. Add a new service definition for your new service.

#### Example:
```yaml
services:
  my-new-service:
    build:
      context: ./services/my-new-service
    image: my-new-service:latest
    container_name: my-new-service
    ports:
      - "5001:5001"  # Map the container's port to a unique host port
    environment:
      - SOME_ENV_VAR=example_value
    networks:
      - microservices-network
```

### **Key Fields to Modify**
- **`context`**: Path to your new service's directory.
- **`image`**: Name and tag for your service image (must be unique).
- **`container_name`**: A unique name for your container.
- **`ports`**: Ensure the host port is unique to avoid conflicts with other services.
- **`networks`**: Attach your service to the existing network.

---

### **Step 5: Build and Run Your Service alongside the other services**
1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Start the container:
   ```bash
   docker-compose up
   ```

3. Access your service at `http://localhost:<PORT>`, where `<PORT>` is the host port you specified in `docker-compose.yml`.

4. **Note**: When services are part of a Docker network, you cannot use localhost to communicate between containers. Instead:

Use the container name (as defined in docker-compose.yml) as the hostname.
For example, if your Spring Boot service is named example-spring-service, other services in the same network can access it at http://example-spring-service:<PORT>.


---

## **Best Practices**

1. **Unique Port Numbers**:
   - Always choose a unique port for your service to avoid conflicts.
   - Update the `EXPOSE` directive in the `Dockerfile` and the `ports` mapping in `docker-compose.yml`.

2. **Environment Variables**:
   - Use environment variables in the `docker-compose.yml` file to configure your service. For example:
     ```yaml
     environment:
       - DATABASE_URL=postgresql://user:password@db:5432/mydb
     ```

3. **Shared Resources**:
   - If your service depends on shared configurations or libraries, place them in the `shared/` directory and mount them as volumes in `docker-compose.yml`.

4. **Logs and Debugging**:
   - Use `docker logs <container_name>` to debug issues.
   - Keep your logs meaningful to simplify troubleshooting.

5. **Testing**:
   - Test your service independently before integrating it into the larger system.

---


## **Next Steps**
1. **Add Your Service**:
   - Follow the steps above to set up your service and integrate it with the project.
2. **Test Connectivity**:
   - If your service interacts with others, test inter-service communication using container names (e.g., `http://example-spring-service:8080`) — This is only for inter container communication. Use `http://localhost:8100/api/v1/users` to test on your local browser.
   - **Note**: When services are part of a Docker network, you cannot use localhost to communicate between containers. Instead:
3. **Document Your Service**:
   - Update this README or create a new one in your service's directory to document its purpose, endpoints, and configuration.
