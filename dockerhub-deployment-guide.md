# Docker Hub + VPS Deployment Guide

## Step 1: Create Docker Hub Account
1. Go to: https://hub.docker.com/
2. Create free account
3. Create repository: cryptovault-hw4

## Step 2: Push Images to Docker Hub
```bash
# Login to Docker Hub
docker login

# Tag images
docker tag cryptovault-hw4/frontend:latest yourusername/cryptovault-hw4-frontend:latest
docker tag cryptovault-hw4/api-gateway:latest yourusername/cryptovault-hw4-api-gateway:latest
docker tag cryptovault-hw4/price-service:latest yourusername/cryptovault-hw4-price-service:latest
docker tag cryptovault-hw4/ta-service:latest yourusername/cryptovault-hw4-ta-service:latest
docker tag cryptovault-hw4/prediction-service:latest yourusername/cryptovault-hw4-prediction-service:latest

# Push images
docker push yourusername/cryptovault-hw4-frontend:latest
docker push yourusername/cryptovault-hw4-api-gateway:latest
docker push yourusername/cryptovault-hw4-price-service:latest
docker push yourusername/cryptovault-hw4-ta-service:latest
docker push yourusername/cryptovault-hw4-prediction-service:latest
```

## Step 3: Deploy to VPS
```bash
# On your VPS:
git clone https://gitlab.finki.ukim.mk/yourusername/homework-4.git
cd homework-4

# Update docker-compose.prod.yml with your Docker Hub username
# Replace cryptovault-hw4 with yourusername

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Your VPS URL:
- **Application**: http://your-server-ip
- **API Gateway**: http://your-server-ip:8080
