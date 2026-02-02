#!/bin/bash

# Deploy to Azure Web App
echo "Deploying CryptoVault Analytics to Azure..."

# Navigate to project directory
cd "/Users/dragananiseva/Downloads/hw-4 repo/homework-4"

# Deploy using Azure CLI
az webapp up \
    --resource-group CryptoVault_group-a7e8 \
    --name CryptoVault \
    --location "Norway East" \
    --sku B1 \
    --runtime "PYTHON:3.9" \
    --src-path "./azure-deploy-package" \
    --os-type Linux

echo "Deployment completed!"
echo "Your app should be available at: https://cryptovault-h8fbc3gxeraxh0ct.norwayeast-01.azurewebsites.net"
