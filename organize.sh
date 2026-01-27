#!/bin/bash

PROJECT_DIR="/Users/dragananiseva/Desktop/homework-4"

echo "🏗️  Organizing project structure..."
mkdir -p "$PROJECT_DIR/services/price_service"
mkdir -p "$PROJECT_DIR/services/ta_service"
mkdir -p "$PROJECT_DIR/services/prediction_service"
mkdir -p "$PROJECT_DIR/api_gateway"
mkdir -p "$PROJECT_DIR/frontend/src/components"
mkdir -p "$PROJECT_DIR/data"

# Move files to correct locations
mv "$PROJECT_DIR/price_service.py" "$PROJECT_DIR/services/price_service/app.py" 2>/dev/null
mv "$PROJECT_DIR/price_service_requirements.txt" "$PROJECT_DIR/services/price_service/requirements.txt" 2>/dev/null

mv "$PROJECT_DIR/ta_service.py" "$PROJECT_DIR/services/ta_service/app.py" 2>/dev/null
mv "$PROJECT_DIR/ta_service_requirements.txt" "$PROJECT_DIR/services/ta_service/requirements.txt" 2>/dev/null

mv "$PROJECT_DIR/prediction_service_app.py" "$PROJECT_DIR/services/prediction_service/app.py" 2>/dev/null
mv "$PROJECT_DIR/prediction_service_requirements.txt" "$PROJECT_DIR/services/prediction_service/requirements.txt" 2>/dev/null

mv "$PROJECT_DIR/GatewayApplication.java" "$PROJECT_DIR/api_gateway/" 2>/dev/null
mv "$PROJECT_DIR/pom.xml" "$PROJECT_DIR/api_gateway/" 2>/dev/null
mv "$PROJECT_DIR/application.yml" "$PROJECT_DIR/api_gateway/" 2>/dev/null

mv "$PROJECT_DIR/App.jsx" "$PROJECT_DIR/frontend/src/" 2>/dev/null
mv "$PROJECT_DIR/PriceChart.jsx" "$PROJECT_DIR/frontend/src/components/" 2>/dev/null
mv "$PROJECT_DIR/TechnicalAnalysisPanel.jsx" "$PROJECT_DIR/frontend/src/components/" 2>/dev/null
mv "$PROJECT_DIR/PredictionPanel.jsx" "$PROJECT_DIR/frontend/src/components/" 2>/dev/null
mv "$PROJECT_DIR/ServiceMonitor.jsx" "$PROJECT_DIR/frontend/src/components/" 2>/dev/null
mv "$PROJECT_DIR/package.json" "$PROJECT_DIR/frontend/" 2>/dev/null
mv "$PROJECT_DIR/frontend_Dockerfile" "$PROJECT_DIR/frontend/Dockerfile" 2>/dev/null
mv "$PROJECT_DIR/nginx.conf" "$PROJECT_DIR/frontend/" 2>/dev/null

mv "$PROJECT_DIR/ETHUSDT.jsonl" "$PROJECT_DIR/data/" 2>/dev/null
mv "$PROJECT_DIR/XLMUSDC.jsonl" "$PROJECT_DIR/data/" 2>/dev/null
mv "$PROJECT_DIR/LINKUSDC.jsonl" "$PROJECT_DIR/data/" 2>/dev/null

# Create missing Dockerfiles
cat > "$PROJECT_DIR/services/price_service/Dockerfile" << 'DOCKERFILE'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY data/ ./data/ 2>/dev/null || true
EXPOSE 5001
CMD ["python", "app.py"]
DOCKERFILE

cat > "$PROJECT_DIR/services/ta_service/Dockerfile" << 'DOCKERFILE'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5002
CMD ["python", "app.py"]
DOCKERFILE

cat > "$PROJECT_DIR/services/prediction_service/Dockerfile" << 'DOCKERFILE'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5003
CMD ["python", "app.py"]
DOCKERFILE

cat > "$PROJECT_DIR/api_gateway/Dockerfile" << 'DOCKERFILE'
FROM maven:3.8.1-openjdk-11-slim as builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY . .
RUN mvn clean package -DskipTests

FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
DOCKERFILE

echo "✅ Project organized!"
