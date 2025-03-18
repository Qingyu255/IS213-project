# Stage 1: Build the application using Maven with JDK 17
FROM maven:3.9.2-eclipse-temurin-17 AS builder
WORKDIR /app

# Copy pom.xml and source code
COPY pom.xml .
# Download dependencies (this layer is cached if pom.xml is unchanged)
RUN mvn dependency:go-offline

# Copy the rest of the source code
COPY src ./src

# Build the application (skip tests for faster build if desired)
RUN mvn clean package -DskipTests

# Stage 2: Create the runtime image
FROM eclipse-temurin:21-jre-alpine

# Set JAVA_HOME and update PATH
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="$PATH:$JAVA_HOME/bin"

# Create an application directory and add a non-root user 'app'
RUN mkdir /app && \
    addgroup --system app && \
    adduser -S -s /bin/false -G app app

WORKDIR /app

# Copy the jar from the builder stage; assumes your jar is in target/ and matches *.jar
COPY --chown=app:app --from=builder /app/target/*.jar /app/app.jar

VOLUME /tmp

# Use non-root user
USER app

# Start the application
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-jar", "/app/app.jar"]
