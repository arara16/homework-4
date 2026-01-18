FROM maven:3.8.6-openjdk-11 as builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=5s --retries=3 CMD curl -f http://localhost:8080/api/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
