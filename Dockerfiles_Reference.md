# Price Service Dockerfile
# services/price_service/Dockerfile

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY data/ data/

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# Run application
CMD ["python", "app.py"]

---

# TA Service Dockerfile
# services/ta_service/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5002

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5002/api/health || exit 1

CMD ["python", "app.py"]

---

# Prediction Service Dockerfile
# services/prediction_service/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY lstm_model.py .
COPY models/ models/

EXPOSE 5003

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5003/api/health || exit 1

CMD ["python", "app.py"]

---

# API Gateway Dockerfile
# api_gateway/Dockerfile

FROM maven:3.8-openjdk-11 AS builder

WORKDIR /app
COPY pom.xml .
COPY src src/

RUN mvn clean package -DskipTests

FROM openjdk:11-jre-slim

WORKDIR /app
COPY --from=builder /app/target/api-gateway-1.0.0.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]

---

# Frontend Dockerfile
# frontend/Dockerfile

FROM node:16-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]