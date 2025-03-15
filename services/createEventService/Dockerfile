# Build stage
FROM jelastic/maven:3.9.5-openjdk-21 AS build
WORKDIR /app

# Copy only the pom file to leverage Docker cache
COPY pom.xml .
# Resolve dependencies in batch mode and with parallel build
RUN mvn dependency:go-offline -B -T 1C

# Copy source code and build in batch mode with parallel builds
COPY src ./src
RUN mvn package -DskipTests -B -T 1C

# Runtime stage
FROM amazoncorretto:21.0.4-alpine3.18
WORKDIR /app

# Copy the packaged jar from the build stage
COPY --from=build /app/target/*.jar app.jar

# Spring Boot reads SERVER_PORT from environment
ENV SERVER_PORT=8070

EXPOSE 8070

ENTRYPOINT ["java", "-jar", "app.jar"]
