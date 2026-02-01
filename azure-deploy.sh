#!/bin/bash

# Azure Deployment Script for CryptoVault Analytics
echo "🚀 Deploying to Azure Web Apps..."

# Configuration
RESOURCE_GROUP="cryptovault-rg"
LOCATION="norwayeast"
APP_PLAN="cryptovault-plan"
APP_NAME="cryptovault-h8fbc3gxeraxh0ct"

echo "📦 Building Docker images for Azure..."

# Build monolithic app for Azure
docker build -f Dockerfile.homework3 -t $APP_NAME.azurewebsites.net/cryptovault:latest .

# Tag for Azure Container Registry
docker tag $APP_NAME.azurewebsites.net/cryptovault:latest $APP_NAME.azurewebsites.net/cryptovault:latest

echo "🔧 Configuring Azure Web App..."

# Create resource group if it doesn't exist
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Create app service plan if it doesn't exist
az appservice plan create \
  --name $APP_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux \
  --output none

# Configure web app
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_PLAN \
  --name $APP_NAME \
  --runtime "PYTHON|3.9" \
  --deployment-container-image-name $APP_NAME.azurewebsites.net/cryptovault:latest \
  --output none

# Set environment variables
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    WEBSITES_PORT=5001 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    DOCKER_CUSTOM_IMAGE_NAME=$APP_NAME.azurewebsites.net/cryptovault:latest \
    DOCKER_CUSTOM_IMAGE_REGISTRY_SERVER_URL=https://$APP_NAME.azurewebsites.net \
  --output none

# Configure CORS
az webapp cors add \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --allowed-origins "*" \
  --output none

echo "🚀 Deploying to Azure..."

# Deploy the container
az webapp config container set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --docker-custom-image-name $APP_NAME.azurewebsites.net/cryptovault:latest \
  --docker-registry-server-url https://$APP_NAME.azurewebsites.net \
  --output none

echo "⏳ Waiting for deployment to complete..."
sleep 30

echo "🔍 Checking deployment status..."
az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query "{name:name, state:state, hostNames:hostNames[0]}" \
  --output table

echo "✅ Deployment complete!"
echo "🌐 Your application is available at: https://$APP_NAME.azurewebsites.net"

# Test the deployment
echo "🧪 Testing deployment..."
curl -f https://$APP_NAME.azurewebsites.net/api/health || echo "❌ Health check failed"

echo "🎉 Azure deployment completed successfully!"
