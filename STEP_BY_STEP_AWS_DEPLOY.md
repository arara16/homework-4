# 🚀 Step-by-Step AWS Educate Deployment – CryptoVault Analytics

## Prerequisites
- AWS Educate account and credentials
- `cryptovault-analytics-eb.zip` (created in your project folder)

---

## Step 1: Log in to AWS Educate
1. Go to: https://aws.amazon.com/education/awseducate/
2. Enter your AWS Educate credentials
3. Click **Login → AWS Management Console**

---

## Step 2: Navigate to Elastic Beanstalk
1. In the AWS Console search bar, type: **Elastic Beanstalk**
2. Click the Elastic Beanstalk service

---

## Step 3: Create a New Application
1. Click **Create application**
2. **Application name**: `CryptoVault-Analytics`
3. **Platform**: Select **Docker**
4. **Application code**: Choose **Upload your code**
5. Click **Choose file** and select `cryptovault-analytics-eb.zip` from your project folder
6. Click **Create application**

---

## Step 4: Wait for Deployment
1. Deployment will take ~5–10 minutes
2. Watch the status:
   - **Launching** → **Updating** → **Environment health: OK**
3. You can view logs if needed (click the environment name → Logs)

---

## Step 5: Open Your Deployed App
1. Once the environment health is **OK**, click the URL at the top
   - Example: `http://CryptoVault-Analytics.xxx.elasticbeanstalk.com`
2. Verify the app works:
   - Homepage loads with symbols list
   - Click **Analyze** on any coin (e.g., BTCUSDT)
   - 7D/30D/90D buttons update charts
   - Charts render correctly
   - No `[object Object]` anywhere
   - On-chain metrics show real values

---

## Step 6: Troubleshooting (if needed)
- **If deployment fails**:
  - Go to Elastic Beanstalk → Your environment → Logs
  - Check Request logs and EB logs for errors
- **If 404s on static files**:
  - Ensure `.ebextensions/python.config` exists in your zip
- **If charts don’t render**:
  - Open browser console (F12)
  - Check for network errors when fetching `/api/analysis/complete/...`

---

## Step 7: Clean Up (optional)
When you’re done:
1. Go to Elastic Beanstalk → Your environment
2. Click **Actions** → **Terminate environment**
3. Confirm termination

---

## What’s in the Zip
- `app.py` – Flask backend with real Binance data, indicators, LSTM-like forecast, sentiment, on-chain metrics
- `static/` – Frontend (HTML/JS/CSS) with Chart.js, fixed `[object Object]` rendering
- `requirements.txt` – Python dependencies (Flask, pandas, numpy, ta, requests, gunicorn)
- `Dockerfile` – Production-ready container (Python 3.12, gunicorn, health check)
- `.ebextensions/python.config` – EB Python config (WSGI, env vars, static files)

---

**You’re done!** Your CryptoVault Analytics platform is now live on AWS Elastic Beanstalk.
