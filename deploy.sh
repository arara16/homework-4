#!/bin/bash

# Homework 4 Deployment Script
echo "🚀 Starting Homework 4 Deployment..."

# Configuration
DOCKER_USERNAME="yourusername"
PROJECT_NAME="homework-4"

echo "📦 Building Docker images..."

# Build all services
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-api-gateway:latest ./api_gateway
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest ./frontend
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-price-service:latest ./services/price_service
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-ta-service:latest ./services/ta_service
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-prediction-service:latest ./services/prediction_service

echo "📤 Pushing to Docker Hub..."

# Push to Docker Hub
docker push $DOCKER_USERNAME/$PROJECT_NAME-api-gateway:latest
docker push $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest
docker push $DOCKER_USERNAME/$PROJECT_NAME-price-service:latest
docker push $DOCKER_USERNAME/$PROJECT_NAME-ta-service:latest
docker push $DOCKER_USERNAME/$PROJECT_NAME-prediction-service:latest

echo "🎯 Deploying to production..."

# Deploy using production compose
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Deployment complete!"
echo "🌐 Application available at: http://your-server-ip"

# Show status
docker-compose -f docker-compose.prod.yml ps

echo "📊 Checking service health..."
sleep 10

# Health checks
curl -f http://localhost/api/health || echo "❌ API Gateway health check failed"
curl -f http://localhost/api/symbols || echo "❌ Symbols endpoint failed"

echo "🎉 Deployment verification complete!"
