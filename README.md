# Проект – Насоки за стартување (Домашна 1, Домашна 2, Домашна 3 и Домашна 4)

Овој репозиториум содржи:
- **Домашна 1:** pipe-and-filter проток за преземање/форматирање на податоци и полнење SQLite база
- **Домашна 2:** технички прототип (React) + Django REST backend кој ги чита податоците од истата база
- **Домашна 3:** анализа и визуелизација (Technical analysis, LSTM предвидување и On-Chain + сентимент анализа) интегрирани во апликацијата
- **Домашна 4:** рефакторирање на архитектурата во микросервиси (FastAPI) и интеграција преку Django proxy

---

Една база за сите:
- Единствена база: `Домашна 1/crypto.db`
- Pipeline (Домашна 1) **ПИШУВА** во оваа база.
- Django backend (Домашна 2, 3, 4) **ЧИТА** од истата база.
- Микросервисите (Домашна 4) исто така пристапуваат до `crypto.db` за анализа.

---

1) Претпоставки/потреби
- Инсталиран **Python 3.11+** (Windows/PowerShell)
- **Node.js 18+** (за фронтенд)
- Интернет конекција (CoinGecko REST, Yahoo Finance API)

---

2) Како да се стартува Домашна 1 (pipeline)?
Локација: `Домашна 1`

PowerShell команди (од коренот на репото):
### 2.1 (Опционално) Креирај виртуелно окружување

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2.2 Инсталирај зависности за филтрите (ако е потребно):

```powershell
pip install -r "Домашна 1\requirements.txt"
```

### 2.3 Стартувај цел pipeline (Filter1 → Filter2 → Filter3 + тајмер)

```powershell
cd "Домашна 1"
python run_all_filters.py
```

Што прави pipeline-от:
- Filter 1: автоматски презема листа на ТОП 1000 активни крипто симболи (филтрира ликвидност/quote и верифицира пазари).
- Filter 2: проверува до кој датум има податоци, презема 15 години OHLCV ако нема, додава 24h метрики, ликвидност.
- Filter 3: пополнува недостигачи денови по пазари и (ако постои USDT‑M фјучерс пар) снима моментален извештај за ликвидации.
- Сè се запишува во `Домашна 1/crypto.db`.

Брзи проверки во SQLite (опционално):

```sql
sqlite3 "Домашна 1/crypto.db"
.tables
SELECT COUNT(*) FROM prices;
.quit
```
---
3) Како да се стартува Домашна 2 (backend + UI)?

### 3.1 Django backend
Локација: `Домашна 2/tech prototype/backend`
PowerShell команди:

```powershell
cd "Домашна 2/tech prototype/backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

Backend слуша на http://localhost:8000 и чита од „Домашна 1/crypto.db“.
Ендпоинти:
- GET /api/health/
- GET /api/summary/
- GET /api/tickers/?limit=50
- GET /api/candles/BTC/?quote=USDT&limit=120

### 3.2 React фронтенд
Локација: Домашна 2/tech prototype
PowerShell команди:

```powershell
cd "Домашна 2/tech prototype"
npm install
npm start
```

---
4) Како да се стартува Домашна 3?
Домашна 3 **нема посебен сервер** – логиката е интегрирана во постоечкиот Django backend и React UI.

### 4.1 Django backend
Локација: `Домашна 3/backend`
PowerShell команди:

```powershell
cd "Домашна 3/backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

### 4.2 React фронтенд
Локација: Домашна 3/frontend
PowerShell команди:

```powershell
cd "Домашна 3/frontend"
npm install
npm start
```

UI слуша на http://localhost:3000 и прави повици кон backend-от на http://localhost:8000/api.

---
5) Како да се стартува Домашна 4 (Microservices)?
Во оваа фаза апликацијата е поделена на 4 микросервиси базирани на **FastAPI**.

### 5.1 Стартување на Микросервисите
Потребно е да се стартуваат 4 посебни сервиси во различни терминали:

```powershell
# 1. Technical Analysis Service (Port 8001)
cd "Домашна 4\technical-analysis-service"
pip install -r requirements.txt
uvicorn main:app --port 8001

# 2. LSTM Prediction Service (Port 8002)
cd "Домашна 4\lstm-service"
pip install -r requirements.txt
uvicorn main:app --port 8002

# 3. Sentiment Analysis Service (Port 8003)
cd "Домашна 4\sentiment-analysis-service"
pip install -r requirements.txt
uvicorn main:app --port 8003

# 4. Notification Service (Port 8004)
cd "Домашна 4\notification-service"
pip install -r requirements.txt
uvicorn main:app --port 8004
```

### 5.2 Django Backend (Proxy)
Локација: `Домашна 4/backend`
Django сега служи како **Proxy** кој ги препраќа барањата до соодветните микросервиси.

```powershell
cd "Домашна 4/backend"
pip install -r requirements.txt
python manage.py runserver 8000
```

### 5.3 React Frontend
Локација: Домашна 4/frontend

```powershell
cd "Домашна 4/frontend"
npm install
npm start
```
# Updated for Vercel redeploy Wed Feb  4 04:29:41 CET 2026
