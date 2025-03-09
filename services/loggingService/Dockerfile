# Use official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Copy the application files into the container
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the service runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "logging_service.py"]
