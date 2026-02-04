# 🚀 Step-by-Step Azure Deployment – CryptoVault Analytics

## Prerequisites
- Azure account (Azure for Students or regular)
- `cryptovault-azure-fixed.zip` (or create a new zip with Azure-ready files)

---

## Step 1: Log in to Azure Portal
1. Go to: https://portal.azure.com
2. Sign in with your Azure credentials

---

## Step 2: Create a New Web App
1. In the top search bar, type: **App Services**
2. Click **Create** → **App Service**
3. **Basics tab**:
   - **Subscription**: Choose your subscription
   - **Resource group**: Create new (e.g., `CryptoVault-RG`)
   - **Name**: `cryptovault-analytics` (must be unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.9
   - **Operating system**: Linux
   - **Region**: Choose nearest (e.g., East US)
   - **App Service Plan**: Create new (e.g., `CryptoVault-Plan`)
   - **Sku and size**: Free F1 or Basic B1 (B1 recommended)
4. Click **Review + create**, then **Create**

---

## Step 3: Configure Deployment Settings
1. After the App Service is created, go to the resource
2. In the left menu, click **Configuration**
3. **Application settings**:
   - Add new setting:
     - Name: `WEBSITES_PORT`
     - Value: `5000`
4. Click **Save** at the top

---

## Step 4: Deploy Your Code
### Option A: Zip Deploy (recommended)
1. In the left menu, click **Deployment Center**
2. Click **Local Git** (if not already selected), then **Save**
3. Scroll down to **Deployment Center** → **FTP/Credentials**
4. Copy **FTP hostname**, **Username**, and **Password**
5. Use an FTP client (like FileZilla) or Azure CLI to upload:
   - Upload `cryptovault-azure-fixed.zip` to `/site/wwwroot/`
   - Extract the zip contents in the portal (use Kudu console)

### Option B: GitHub Actions (advanced)
1. Push your code to GitHub
2. In Deployment Center, select **GitHub**
3. Authorize GitHub, select your repo and branch
4. Azure will auto-build and deploy

---

## Step 5: Verify Deployment
1. Go to your App Service Overview
2. Click the **URL** (e.g., `https://cryptovault-analytics.azurewebsites.net`)
3. Verify:
   - Homepage loads with symbols list
   - Click **Analyze** on any coin
   - 7D/30D/90D buttons work
   - Charts render
   - No `[object Object]` anywhere

---

## Step 6: Troubleshooting
- **If 500 errors**:
  - Go to **Diagnose and solve problems** → **Web App Down**
  - Check **Log stream** for errors
- **If static files 404**:
  - Ensure `static/` folder is at the root
  - Check `web.config` for static file handling
- **If app won’t start**:
  - Check **App Service Logs** → **Log stream**
  - Verify `requirements.txt` includes all dependencies

---

## Step 7: Clean Up (optional)
When done:
1. Go to your Resource Group
2. Click **Delete resource group**
3. Confirm deletion

---

## What’s in the Azure Zip
- `app.py` or `azure-app.py` – Flask backend
- `static/` – Frontend files
- `requirements.txt` – Python dependencies
- `web.config` – Azure IIS configuration
- `startup.sh` or `startup-azure.sh` – Startup script

---

**You’re done!** Your CryptoVault Analytics is now live on Azure App Service.
