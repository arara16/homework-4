# Homework 4 - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#setup)
4. [Running the Application](#running)
5. [API Documentation](#api)
6. [Design Patterns](#patterns)
7. [Cloud Deployment](#cloud)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Overview

**CryptoVault HW4** is a complete implementation of a microservices-based cryptocurrency analysis platform featuring:

✅ **Microservices Architecture** - Separated concerns across multiple services  
✅ **Strategy Design Pattern** - Pluggable data sources and algorithms  
✅ **Docker Containerization** - Production-ready deployment  
✅ **React Frontend** - Modern, responsive user interface  
✅ **Technical Analysis** - RSI, MACD, Bollinger Bands, Moving Averages  
✅ **LSTM Predictions** - Deep learning price forecasting  
✅ **API Gateway** - Centralized request routing and aggregation  

**Deadline**: January 9, 2026 ✓

---

## Architecture

### High-Level System Design

```
┌──────────────────────────────────────────────────────────────┐
│                    Browser / Client                          │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼───────────────────────────────────────┐
│         API Gateway (Spring Boot - Port 8080)               │
│  ├─ Request routing                                          │
│  ├─ Load balancing                                           │
│  ├─ Circuit breaking                                         │
│  └─ Rate limiting                                            │
└─────┬────────────┬──────────────────┬──────────────────────┘
      │            │                  │
      ▼            ▼                  ▼
┌──────────┐  ┌──────────┐  ┌──────────────────┐
│ Price    │  │TA Service│  │ Prediction       │
│ Service  │  │(Port5002)│  │Service(Port5003) │
│(Port5001)│  └──────────┘  └──────────────────┘
└──────────┘
      │            │                  │
      └────────────┴──────────────────┘
                   │
        ┌──────────┴─────────┐
        │                    │
        ▼                    ▼
   ┌────────────┐      ┌──────────┐
   │ PostgreSQL │      │  Redis   │
   │ (Port 5432)│      │Cache     │
   └────────────┘      │(Port6379)│
                       └──────────┘
```

### Service Responsibilities

| Service | Port | Tech | Responsibility |
|---------|------|------|-----------------|
| **Price Service** | 5001 | Flask | OHLCV data, multi-source strategy |
| **TA Service** | 5002 | Flask | Technical indicators (RSI, MACD, BB, MA) |
| **Prediction Service** | 5003 | Flask + TensorFlow | LSTM predictions |
| **API Gateway** | 8080 | Spring Boot | Request routing, aggregation |
| **Frontend** | 3000 | React | User interface |
| **PostgreSQL** | 5432 | - | Persistent data storage |
| **Redis** | 6379 | - | Caching layer |

---

## Installation & Setup

### Prerequisites
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.9+ (for local development)
- **Node.js** 16+ (for frontend development)
- **Java** 11+ (for API Gateway)

### Project Structure

```
homework-4/
├── services/
│   ├── price_service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── data/
│   │       ├── ETHUSDT.jsonl
│   │       ├── XLMUSDC.jsonl
│   │       └── LINKUSDC.jsonl
│   │
│   ├── ta_service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── prediction_service/
│       ├── app.py
│       ├── lstm_model.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── api_gateway/
│   ├── pom.xml
│   ├── src/main/java/com/cryptovault/
│   │   ├── GatewayApplication.java
│   │   ├── config/
│   │   ├── controller/
│   │   └── service/
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
├── init_db.sql
├── DESIGN_PATTERN.md
├── API_DOCUMENTATION.md
└── README.md
```

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://gitlab.finki.ukim.mk/236041/homework-4.git
cd homework-4

# Create necessary directories
mkdir -p data models
```

### Step 2: Configure Environment

Create `.env` file in root:

```env
# Database
POSTGRES_USER=cryptovault
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=cryptovault_db

# Services
FLASK_ENV=production
SPRING_PROFILES_ACTIVE=docker

# API Configuration
API_GATEWAY_PORT=8080
PRICE_SERVICE_PORT=5001
TA_SERVICE_PORT=5002
PREDICTION_SERVICE_PORT=5003

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Frontend
REACT_APP_API_GATEWAY=http://localhost:8080/api
NODE_ENV=production
```

### Step 3: Build and Run with Docker

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 4: Verify Services

```bash
# Check Price Service
curl http://localhost:5001/api/health

# Check TA Service
curl http://localhost:5002/api/health

# Check Prediction Service
curl http://localhost:5003/api/health

# Check API Gateway
curl http://localhost:8080/api/health

# Access Frontend
open http://localhost:3000
```

---

## Running the Application

### Option 1: Docker Compose (Production)

```bash
# Start all services
docker-compose up -d

# View logs for all services
docker-compose logs -f

# Stop all services
docker-compose down

# Remove volumes (for fresh database)
docker-compose down -v
```

### Option 2: Local Development

```bash
# Terminal 1: Price Service
cd services/price_service
pip install -r requirements.txt
python app.py

# Terminal 2: TA Service
cd services/ta_service
pip install -r requirements.txt
python app.py

# Terminal 3: Prediction Service
cd services/prediction_service
pip install -r requirements.txt
python app.py

# Terminal 4: API Gateway
cd api_gateway
./mvnw spring-boot:run

# Terminal 5: Frontend
cd frontend
npm install
npm start
```

---

## API Documentation

### Base URL
- **Production**: `http://localhost:8080/api`
- **Development**: `http://localhost:5001/api` (direct to services)

### Price Service Endpoints

#### Get OHLCV Data
```
GET /prices/<symbol>
Query Parameters:
  - timeframe: string (default: 1h)
  - limit: integer (default: 100)

Example:
curl "http://localhost:8080/api/prices/ETHUSDT?timeframe=1h&limit=100"

Response:
{
  "symbol": "ETHUSDT",
  "timeframe": "1h",
  "data": [
    {
      "time": 1641234000000,
      "open": 2500.5,
      "high": 2510.2,
      "low": 2495.1,
      "close": 2505.3,
      "volume": 150.5
    },
    ...
  ],
  "source": "File (Historical)",
  "count": 100
}
```

#### Get Latest Price
```
GET /prices/latest/<symbol>

Response:
{
  "symbol": "ETHUSDT",
  "price": 2505.3,
  "timestamp": 1641234000000,
  "source": "File (Historical)"
}
```

#### Get Price Statistics
```
GET /prices/stats/<symbol>

Response:
{
  "symbol": "ETHUSDT",
  "current_price": 2505.3,
  "high": 2510.2,
  "low": 2495.1,
  "avg": 2502.8,
  "change": 1.25,
  "count": 30
}
```

### Technical Analysis Service Endpoints

#### Get All Indicators
```
GET /technical-analysis/<symbol>

Response:
{
  "symbol": "ETHUSDT",
  "indicators": {
    "rsi": {
      "indicator": "RSI",
      "value": 65.5,
      "overbought": false,
      "oversold": false,
      "period": 14
    },
    "macd": {
      "indicator": "MACD",
      "macd_line": 150.2,
      "signal_line": 145.8,
      "histogram": 4.4,
      "bullish": true
    },
    "bb": {
      "indicator": "Bollinger Bands",
      "upper_band": 2520.5,
      "middle_band": 2505.0,
      "lower_band": 2489.5,
      "position": "neutral"
    },
    "ma": {
      "indicator": "Moving Averages",
      "sma_short": 2508.0,
      "sma_long": 2502.0,
      "trend": "bullish"
    }
  }
}
```

#### Get Trading Signal
```
GET /signal/<symbol>

Response:
{
  "symbol": "ETHUSDT",
  "signal": "BUY",
  "confidence": 0.85,
  "score": 2
}
```

### Prediction Service Endpoints

#### Get Price Prediction
```
GET /predict/<symbol>
Query Parameters:
  - days: integer (default: 7)

Response:
{
  "symbol": "ETHUSDT",
  "predictions": [
    {
      "day": 1,
      "price": 2510.5,
      "confidence": 0.92
    },
    ...
  ],
  "model_version": "LSTM_v1.0"
}
```

---

## Design Patterns

### Strategy Pattern Implementation

The application uses **Strategy Pattern** to make data sources and algorithms interchangeable:

#### Price Service Strategy
```python
# Abstract Strategy
class PriceDataStrategy(ABC):
    @abstractmethod
    def fetch_ohlcv(self, symbol, timeframe, limit) -> list:
        pass

# Concrete Strategies
class FileDataStrategy(PriceDataStrategy): ...  # JSONL files
class APIDataStrategy(PriceDataStrategy): ...   # Live API
class CacheStrategy(PriceDataStrategy): ...     # Redis cache

# Context using strategies
manager = PriceDataManager()
manager.add_strategy(cache_strategy)
manager.add_strategy(file_strategy)
manager.add_strategy(api_strategy)
```

**Benefits**:
- Switch data sources without code changes
- Fallback mechanism (cache → file → API)
- Easy to test with mock strategies
- Open/Closed Principle compliance

#### TA Service Strategy
```python
# Abstract Strategy
class TAStrategy(ABC):
    @abstractmethod
    def calculate(self, prices: list) -> dict:
        pass

# Concrete Strategies
class RSIStrategy(TAStrategy): ...
class MACDStrategy(TAStrategy): ...
class BollingerBandsStrategy(TAStrategy): ...
```

---

## Cloud Deployment

### Azure Deployment

```bash
# 1. Create resource group
az group create --name cryptovault-rg --location eastus

# 2. Create App Service plan
az appservice plan create \
  --name cryptovault-plan \
  --resource-group cryptovault-rg \
  --sku B2 --is-linux

# 3. Deploy each service
az webapp create \
  --resource-group cryptovault-rg \
  --plan cryptovault-plan \
  --name cryptovault-price \
  --deployment-container-image-name cryptovault-price:latest

# 4. Set environment variables
az webapp config appsettings set \
  --resource-group cryptovault-rg \
  --name cryptovault-price \
  --settings REDIS_URL=redis://cryptovault-redis.redis.cache.windows.net:6379
```

### AWS Deployment

```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name cryptovault-price
aws ecr create-repository --repository-name cryptovault-ta
aws ecr create-repository --repository-name cryptovault-prediction
aws ecr create-repository --repository-name cryptovault-gateway

# 2. Push images
docker tag cryptovault-price:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/cryptovault-price:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/cryptovault-price:latest

# 3. Deploy to ECS
aws ecs create-cluster --cluster-name cryptovault
# Create task definitions and services...
```

---

## Testing

### Unit Tests

```bash
# Price Service Tests
cd services/price_service
python -m pytest tests/test_strategies.py -v

# TA Service Tests
cd services/ta_service
python -m pytest tests/test_indicators.py -v
```

### Integration Tests

```bash
# Run all services
docker-compose up -d

# Run integration tests
python tests/integration_tests.py

# View coverage
pytest --cov=services tests/
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8080/api/prices/ETHUSDT

# Using k6
k6 run load_test.js
```

---

## Troubleshooting

### Service Health Issues

```bash
# Check service logs
docker-compose logs price-service
docker-compose logs ta-service
docker-compose logs api-gateway

# Check network connectivity
docker network inspect cryptovault_network

# Rebuild service
docker-compose up --build price-service
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker exec cryptovault-postgres psql -U cryptovault -d cryptovault_db

# Reset database
docker-compose down -v
docker-compose up postgres

# Run migrations
python db/migrate.py
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check API latency
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/api/prices/ETHUSDT

# Profile services
python -m cProfile -s cumulative app.py
```

---

## Submission Checklist

✅ Design Pattern Documentation (DESIGN_PATTERN.md)  
✅ Microservices Implementation (4 services)  
✅ Docker Containerization (docker-compose.yml)  
✅ Advanced Frontend (React with real-time updates)  
✅ Technical Analysis (5 indicators)  
✅ LSTM Predictions  
✅ API Documentation  
✅ Cloud Deployment Guides  
✅ Testing Coverage  
✅ README and Documentation  

---

## References

- [Strategy Pattern - Refactoring Guru](https://refactoring.guru/design-patterns/strategy)
- [Microservices Architecture - Martin Fowler](https://martinfowler.com/articles/microservices.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [React Documentation](https://react.dev)
- [Docker Documentation](https://docs.docker.com/)

---

**Version**: 1.0  
**Last Updated**: January 6, 2026  
**Status**: Complete ✓