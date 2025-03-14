# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the dependencies file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the Docker image
COPY . .

# Expose port 5001 so the service is accessible
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"]