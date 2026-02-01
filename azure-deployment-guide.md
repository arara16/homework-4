# Azure Web Apps Deployment Guide

## Step 1: Create Azure Account
1. Go to: https://azure.microsoft.com/en-us/free/students/
2. Sign up with your student email
3. Verify your student status (1-2 days)

## Step 2: Install Azure CLI
```bash
# macOS
brew install azure-cli

# Verify installation
az --version
```

## Step 3: Login and Create Resources
```bash
az login

# Create resource group
az group create \
  --name homework-4-rg \
  --location "East US"

# Create app service plan
az appservice plan create \
  --name homework-4-plan \
  --resource-group homework-4-rg \
  --sku B1 \
  --is-linux

# Create web apps
az webapp create \
  --resource-group homework-4-rg \
  --plan homework-4-plan \
  --name homework-4-frontend \
  --runtime "NODE|18-lts"

az webapp create \
  --resource-group homework-4-rg \
  --plan homework-4-plan \
  --name homework-4-api-gateway \
  --runtime "JAVA|17-java17"

az webapp create \
  --resource-group homework-4-rg \
  --plan homework-4-plan \
  --name homework-4-price-service \
  --runtime "PYTHON|3.9"

az webapp create \
  --resource-group homework-4-rg \
  --plan homework-4-plan \
  --name homework-4-ta-service \
  --runtime "PYTHON|3.9"

az webapp create \
  --resource-group homework-4-rg \
  --plan homework-4-plan \
  --name homework-4-prediction-service \
  --runtime "PYTHON|3.9"
```

## Step 4: Configure Environment Variables
```bash
# Configure API Gateway
az webapp config appsettings set \
  --resource-group homework-4-rg \
  --name homework-4-api-gateway \
  --settings \
    SPRING_PROFILES_ACTIVE=azure \
    PRICE_SERVICE_URL=https://homework-4-price-service.azurewebsites.net \
    TA_SERVICE_URL=https://homework-4-ta-service.azurewebsites.net \
    PREDICTION_SERVICE_URL=https://homework-4-prediction-service.azurewebsites.net

# Configure Frontend
az webapp config appsettings set \
  --resource-group homework-4-rg \
  --name homework-4-frontend \
  --settings \
    REACT_APP_API_URL=https://homework-4-api-gateway.azurewebsites.net/api
```

## Step 5: Deploy Your Images
```bash
# Tag for Azure Container Registry
az acr create \
  --resource-group homework-4-rg \
  --name homework4registry \
  --sku Basic

az acr login --name homework4registry

# Tag and push images
docker tag cryptovault-hw4/frontend:latest homework4registry.azurecr.io/frontend:latest
docker tag cryptovault-hw4/api-gateway:latest homework4registry.azurecr.io/api-gateway:latest
docker tag cryptovault-hw4/price-service:latest homework4registry.azurecr.io/price-service:latest
docker tag cryptovault-hw4/ta-service:latest homework4registry.azurecr.io/ta-service:latest
docker tag cryptovault-hw4/prediction-service:latest homework4registry.azurecr.io/prediction-service:latest

docker push homework4registry.azurecr.io/frontend:latest
docker push homework4registry.azurecr.io/api-gateway:latest
docker push homework4registry.azurecr.io/price-service:latest
docker push homework4registry.azurecr.io/ta-service:latest
docker push homework4registry.azurecr.io/prediction-service:latest

# Deploy to Azure
az webapp create \
  --resource-group homework-4-rg \
  --plan homework-4-plan \
  --name homework-4-frontend \
  --deployment-container-image-name homework4registry.azurecr.io/frontend:latest
```

## Your Azure URLs:
- **Frontend**: https://homework-4-frontend.azurewebsites.net
- **API Gateway**: https://homework-4-api-gateway.azurewebsites.net
- **Price Service**: https://homework-4-price-service.azurewebsites.net
- **TA Service**: https://homework-4-ta-service.azurewebsites.net
- **Prediction Service**: https://homework-4-prediction-service.azurewebsites.net
