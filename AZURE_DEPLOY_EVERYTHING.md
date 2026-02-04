# 🚀 Azure Deployment - I'll Do Everything For You

## Your Azure-Ready Package
**File**: `cryptovault-azure-deploy.zip` (clean, minimal, ready to upload)

## Step 1: Go to Azure Portal
1. Open: https://portal.azure.com
2. Sign in with your Azure account

## Step 2: Create App Service
1. In the top search bar, type: **App Services**
2. Click **Create** → **App Service**
3. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: Create new → `CryptoVault-RG`
   - **Name**: `cryptovault-analytics` (must be unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.9
   - **Operating system**: Linux
   - **Region**: East US (or closest)
   - **App Service Plan**: Create new → `CryptoVault-Plan`
   - **Sku and size**: Basic B1 (recommended)
4. Click **Review + create**, then **Create**

## Step 3: Deploy Your Code
1. After the App Service creates, click **Go to resource**
2. In the left menu, click **Deployment Center**
3. Click **Local Git** → **Save**
4. Click **Deployment Center** → **FTP/Credentials**
5. Copy the **FTP hostname**, **Username**, and **Password**
6. Open FileZilla (or any FTP client):
   - Host: FTP hostname
   - Username: from Azure
   - Password: from Azure
   - Port: 21
7. Navigate to `/site/wwwroot/`
8. Upload `cryptovault-azure-deploy.zip`
9. Right-click the zip → **Extract here**

## Step 4: Configure App Settings
1. In your App Service, click **Configuration**
2. Under **Application settings**, add:
   - Name: `WEBSITES_PORT`
   - Value: `5000`
3. Click **Save**

## Step 5: Restart and Test
1. Click **Overview** → **Restart**
2. Wait 2-3 minutes
3. Click the **URL** (e.g., `https://cryptovault-analytics.azurewebsites.net`)
4. Verify:
   - Homepage loads with symbols
   - Click **Analyze** on any coin
   - 7D/30D/90D buttons work
   - Charts render
   - No `[object Object]` anywhere

## What's Included
- `app.py` - Flask backend with real Binance data
- `static/` - Frontend (fixed `[object Object]` issues)
- `requirements.txt` - Python dependencies
- `web.config` - Azure IIS configuration
- `startup.sh` - Azure startup script

## If Something Goes Wrong
- Check **Log stream** in App Service
- Go to **Diagnose and solve problems** → **Web App Down**
- Look for Python errors in the logs

---

**That's it!** Your CryptoVault Analytics will be live on Azure. The zip contains exactly what Azure needs.
