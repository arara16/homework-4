# 🚀 AWS Educate Deployment Guide – CryptoVault Analytics

## 1️⃣ Upload and Deploy (Elastic Beanstalk)

1. **Login to AWS Educate**
   - Go to: https://aws.amazon.com/education/awseducate/
   - Enter your AWS Educate credentials
   - Click **Login → AWS Management Console**

2. **Navigate to Elastic Beanstalk**
   - In the console search bar, type: **Elastic Beanstalk**
   - Click the service

3. **Create Application**
   - Click **Create application**
   - Application name: `CryptoVault-Analytics`
   - Platform: **Docker**
   - Application code: **Upload your code**
   - Choose file: `cryptovault-analytics-eb.zip`
   - Click **Create application**

4. **Wait for Deploy**
   - Deployment takes ~5–10 minutes
   - Status will change from **Launching** → **Updating** → **Environment health: OK**

5. **Open the App**
   - Once healthy, click the URL at the top (e.g., `http://CryptoVault-Analytics.xxx.elasticbeanstalk.com`)
   - Verify:
     - Symbols list loads
     - Click **Analyze** on any coin
     - 7D/30D/90D buttons work
     - Charts render
     - No `[object Object]` anywhere

---

## 2️⃣ What’s Included in the Zip

- `app.py` – Flask backend with real Binance data, technical indicators, LSTM-like forecast, sentiment, on-chain metrics
- `static/` – Frontend (HTML/JS/CSS) with Chart.js, fixed `[object Object]` rendering
- `requirements.txt` – Python deps (Flask, pandas, numpy, ta, requests, gunicorn)
- `Dockerfile` – Production-ready container (Python 3.12, gunicorn, health check)
- `.ebextensions/python.config` – EB Python config (WSGI, env vars, static files)

---

## 3️⃣ Troubleshooting

- **If deployment fails**:
  - Check Elastic Beanstalk **Logs** (Request logs, EB logs)
  - Common issue: missing `curl` in container (included in Dockerfile health check)
- **If 404s on static files**:
  - Ensure `.ebextensions/python.config` static mapping is present
- **If charts don’t render**:
  - Open browser console; ensure no network errors fetching `/api/analysis/complete/...`

---

## 4️⃣ Post-deploy verification (quick checklist)

- [ ] Homepage loads
- [ ] `/api/symbols` returns 15 USDT pairs
- [ ] Analyze BTCUSDT shows real price, 24h change, volume
- [ ] 7D/30D/90D buttons update charts
- [ ] No `[object Object]` in Technical Indicators or Signals
- [ ] On-chain metrics show non-zero values (transaction_count, active_addresses, nvt_ratio, mvrv)

---

## 5️⃣ Local vs Production

- Local runs on `http://localhost:5005`
- Production will be on `http://<app-name>.<region>.elasticbeanstalk.com`
- All features are identical; only the host changes

---

**You’re ready!** Upload `cryptovault-analytics-eb.zip` to Elastic Beanstalk and follow the steps above.
