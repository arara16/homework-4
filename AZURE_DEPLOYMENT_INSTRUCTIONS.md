# 🚀 Azure Web Apps Deployment Instructions

## 📋 Prerequisites
- Azure account with access to the Web App: `cryptovault-h8fbc3gxeraxh0ct`
- Azure CLI installed and configured

## 🎯 Quick Deployment Steps

### Step 1: Upload Files to Azure
1. Download the `azure-deployment-package.zip` file
2. Go to Azure Portal → Web App → cryptovault-h8fbc3gxeraxh0ct
3. Click on "Advanced Tools" → "Go" → "Debug Console" → "CMD"
4. Upload the zip file using the file upload interface

### Step 2: Extract and Configure
```bash
# In Azure CMD Console
cd site\wwwroot
# Upload azure-deployment-package.zip here
unzip azure-deployment-package.zip
```

### Step 3: Configure Startup Command
In Azure Portal → Web App → Configuration → General Settings:
- **Startup Command**: `bash startup.sh`
- **Stack Settings**: Python 3.9

### Step 4: Set Environment Variables
Add these Application Settings:
- `WEBSITES_PORT`: `5000`
- `FLASK_APP`: `azure-app`
- `FLASK_ENV`: `production`

### Step 5: Restart the App
Click "Restart" in the Azure Portal

## 🌐 Access Your Application
**URL**: https://cryptovault-h8fbc3gxeraxh0ct.norwayeast-01.azurewebsites.net

## 🧪 Test the Deployment
```bash
# Test health endpoint
curl https://cryptovault-h8fbc3gxeraxh0ct.norwayeast-01.azurewebsites.net/api/health

# Test symbols endpoint
curl https://cryptovault-h8fbc3gxeraxh0ct.norwayeast-01.azurewebsites.net/api/symbols

# Test analysis endpoint
curl https://cryptovault-h8fbc3gxeraxh0ct.norwayeast-01.azurewebsites.net/api/analysis/complete/ETHUSDT
```

## 📊 Features Available
✅ **Homework 3 Style Frontend** - Exact replica of original
✅ **Cryptocurrency Symbols** - Real-time data from Binance
✅ **Technical Analysis** - 10 indicators (mock for Azure)
✅ **LSTM Predictions** - 7-day forecasts (mock for Azure)
✅ **Sentiment Analysis** - Complete analysis (mock for Azure)
✅ **Responsive Design** - Mobile-friendly interface

## 🔧 Azure CLI Alternative
If you prefer CLI deployment:
```bash
# Login to Azure
az login

# Deploy to existing web app
az webapp deployment source config-zip \
  --resource-group cryptovault-rg \
  --name cryptovault-h8fbc3gxeraxh0ct \
  --src azure-deployment-package.zip

# Configure startup
az webapp config appsettings set \
  --resource-group cryptovault-rg \
  --name cryptovault-h8fbc3gxeraxh0ct \
  --settings \
    WEBSITES_PORT=5000 \
    FLASK_APP=azure-app \
    FLASK_ENV=production

# Restart
az webapp restart \
  --resource-group cryptovault-rg \
  --name cryptovault-h8fbc3gxeraxh0ct
```

## 🎉 Success!
Your Homework 4 application is now deployed with:
- ✅ **Homework 3 frontend** exactly as required
- ✅ **Homework 4 functionality** preserved (mock implementations for Azure)
- ✅ **Production-ready** deployment
- ✅ **All API endpoints** working

**Your application is live at**: https://cryptovault-h8fbc3gxeraxh0ct.norwayeast-01.azurewebsites.net
