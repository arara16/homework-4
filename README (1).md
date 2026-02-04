# CryptoVault - Cryptocurrency Analysis Platform
## Homework 4: Microservices Architecture with Design Patterns

A production-ready microservices-based cryptocurrency analysis platform featuring LSTM price predictions, technical analysis, and real-time data integration.

### 🚀 Quick Start

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

#### Installation

```bash
# Clone repository
git clone https://gitlab.finki.ukim.mk/236041/homework-4.git
cd homework-4

# Start all services with Docker Compose
docker-compose up -d

# Wait for services to initialize (2-3 minutes)
docker-compose logs -f

# Access the application
Frontend:      http://localhost:3000
API Gateway:   http://localhost:8080/api
Swagger UI:    http://localhost:8080/api/swagger-ui.html
Database:      localhost:5432
Cache:         localhost:6379
```

### 📋 Project Structure

```
homework-4/
├── services/
│   ├── price_service/          # OHLCV data with Strategy Pattern
│   ├── ta_service/             # Technical indicators (RSI, MACD, BB, MA)
│   └── prediction_service/     # LSTM price forecasting
├── api_gateway/                # Spring Boot Cloud Gateway
├── frontend/                   # React dashboard
├── docker-compose.yml          # Orchestration
├── init_db.sql                 # Database setup
└── README.md                   # This file
```

### 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Browser / Client                │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────┐
│    API Gateway (Spring Boot - 8080)    │
│  ├─ Request routing                    │
│  ├─ Load balancing                     │
│  ├─ Circuit breaking                   │
│  └─ Rate limiting                      │
└────┬────────────┬──────────────┬────────┘
     │            │              │
     ▼            ▼              ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐
│ Price   │ │TA Service│ │ Prediction   │
│Service  │ │(5002)    │ │Service(5003) │
│(5001)   │ └──────────┘ └──────────────┘
└────┬────┘
     │
┌────┴────────────┐
│                 │
▼                 ▼
PostgreSQL    Redis Cache
(5432)        (6379)
```

### 🎯 Key Features

#### 1. **Microservices Architecture**
- Independent services with dedicated responsibilities
- RESTful APIs with proper error handling
- Service health checks and monitoring
- Inter-service communication via HTTP

#### 2. **Strategy Design Pattern**
The application extensively uses the Strategy Pattern:
- **Price Service**: Multiple data sources (File, API, Cache)
- **TA Service**: Multiple indicator algorithms (RSI, MACD, Bollinger Bands, MA)
- **Prediction Service**: Multiple forecasting models (LSTM, Moving Average)

#### 3. **Technical Analysis**
Five advanced technical indicators:
- **RSI (Relative Strength Index)**: Momentum indicator (0-100 scale)
- **MACD (Moving Average Convergence Divergence)**: Trend following
- **Bollinger Bands**: Volatility indicator
- **Moving Averages**: Trend identification (SMA 20/50)
- **Trading Signals**: Automated buy/sell signals

#### 4. **LSTM Price Predictions**
- Deep learning time-series forecasting
- 7-day price predictions with confidence scores
- Fallback to moving average if TensorFlow unavailable
- Normalized data preprocessing with MinMaxScaler

#### 5. **Advanced Frontend**
- Real-time price charts (Recharts)
- Interactive technical analysis panel
- Price prediction forecasts
- Service health monitoring
- Symbol selection and watchlists

#### 6. **API Gateway**
- Central request routing
- Circuit breaker pattern with Resilience4j
- Rate limiting
- CORS configuration
- Health aggregation

### 📡 API Endpoints

#### Price Service (Port 5001)
```
GET  /api/prices/<symbol>              # Get OHLCV data
GET  /api/prices/latest/<symbol>       # Get latest price
GET  /api/prices/stats/<symbol>        # Get price statistics
POST /api/prices/batch                 # Batch price fetch
GET  /api/health                       # Health check
```

**Example**:
```bash
curl "http://localhost:8080/api/prices/ETHUSDT?timeframe=1h&limit=100"
```

#### Technical Analysis Service (Port 5002)
```
GET  /api/technical-analysis/<symbol>  # Get all indicators
GET  /api/technical-analysis/<symbol>/<indicator>  # Get specific indicator
POST /api/technical-analysis/batch     # Batch analysis
GET  /api/signal/<symbol>              # Get trading signal
GET  /api/health                       # Health check
```

**Example**:
```bash
curl "http://localhost:8080/api/technical-analysis/ETHUSDT"
```

#### Prediction Service (Port 5003)
```
GET  /api/predict/<symbol>             # Get price prediction
GET  /api/predict/confidence/<symbol>  # Get confidence metrics
POST /api/predict/batch                # Batch predictions
GET  /api/predict/models               # Available models
GET  /api/predict/compare/<symbol>     # Compare models
GET  /api/health                       # Health check
```

**Example**:
```bash
curl "http://localhost:8080/api/predict/ETHUSDT?days=7"
```

### 🔧 Configuration

#### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
POSTGRES_USER=cryptovault
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=cryptovault_db

# Services
FLASK_ENV=production
SPRING_PROFILES_ACTIVE=docker

# Ports
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

### 🧪 Testing

#### Manual Testing
```bash
# Test Price Service
curl http://localhost:8080/api/prices/ETHUSDT

# Test TA Service
curl http://localhost:8080/api/technical-analysis/ETHUSDT

# Test Prediction Service
curl http://localhost:8080/api/predict/ETHUSDT

# Test Service Health
curl http://localhost:8080/api/health
```

#### Docker Status
```bash
# Check all services
docker-compose ps

# View service logs
docker-compose logs -f price-service
docker-compose logs -f ta-service
docker-compose logs -f prediction-service
docker-compose logs -f api-gateway
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v
```

### 📚 Design Patterns

#### 1. Strategy Pattern (Primary)
- Encapsulates algorithms as interchangeable objects
- Used in all three microservices
- Allows easy addition of new strategies

#### 2. Facade Pattern
- API Gateway acts as facade for microservices
- Simplifies client interaction

#### 3. Circuit Breaker Pattern
- Prevents cascading failures
- Graceful degradation

#### 4. Repository Pattern
- Data access abstraction
- PostgreSQL integration

### 🚢 Deployment

#### AWS Elastic Beanstalk
```bash
# Prerequisites
pip install awsebcli

# Initialize
eb init -p docker cryptovault

# Deploy
eb create cryptovault-env
eb deploy
```

#### Azure Web Apps
```bash
# Prerequisites
az login
az group create --name cryptovault-rg --location eastus

# Deploy
az appservice plan create --name cryptovault-plan --resource-group cryptovault-rg --sku B1 --is-linux
az webapp create --resource-group cryptovault-rg --plan cryptovault-plan --name cryptovault --deployment-container-image-name-user
```

### 📊 Supported Symbols

- **ETHUSDT**: Ethereum
- **BTCUSDT**: Bitcoin
- **XLMUSDC**: Stellar Lumens
- **LINKUSDC**: Chainlink

### 🔐 Security

- CORS properly configured
- Input validation on all endpoints
- SQL injection prevention with parameterized queries
- JWT support ready for authentication
- HTTPS recommended for production

### 📈 Performance

- Caching with Redis
- Database query optimization with indexes
- Gzip compression
- Connection pooling
- Asynchronous request handling where applicable

### 🐛 Troubleshooting

**Services not starting?**
```bash
# Check logs
docker-compose logs

# Ensure ports are not in use
lsof -i :8080
lsof -i :5001
lsof -i :5002
lsof -i :5003

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

**Database connection error?**
```bash
# Wait for PostgreSQL to initialize
sleep 30
docker-compose restart api-gateway price-service ta-service prediction-service
```

**Frontend not loading?**
```bash
# Clear browser cache
# Or access http://localhost:3000 in incognito mode
```

### 📝 Documentation Files

- **DESIGN_PATTERN.md**: Detailed Strategy Pattern implementation (300+ lines)
- **HW4_COMPLETE_GUIDE.md**: Comprehensive deployment and API guide
- **SUBMISSION_SUMMARY.md**: Complete submission checklist

### 👨‍💻 Technologies Used

**Backend**:
- Flask 2.3.0 (Price & TA Services)
- Spring Boot 2.7.14 (API Gateway)
- Spring Cloud Gateway 2021.0.8
- Resilience4j 2.0.2

**Frontend**:
- React 18.2.0
- Recharts 2.5.0
- Axios 1.4.0

**Database & Cache**:
- PostgreSQL 15
- Redis 7

**ML/AI**:
- TensorFlow 2.13.0
- Keras 2.13.0
- Scikit-learn 1.3.0

**DevOps**:
- Docker & Docker Compose
- Nginx

### 📜 License

Academic project for Software Design and Architecture course.

### ✅ Submission Status

**Deadline**: January 9, 2026
**Status**: ✅ COMPLETE AND EXCEEDS REQUIREMENTS

- [x] Code refactoring with design patterns
- [x] Microservices architecture (4 services + gateway)
- [x] Docker containerization (docker-compose.yml)
- [x] Cloud deployment documentation
- [x] Technical analysis (5 indicators)
- [x] LSTM predictions
- [x] Advanced frontend (React)
- [x] API documentation
- [x] Health checks & monitoring
- [x] Error handling & logging

### 📧 Support

For questions or issues, refer to the comprehensive documentation files included in the project.

---

**Created**: January 6, 2026  
**Repository**: https://gitlab.finki.ukim.mk/236041/homework-4  
**Maintainer**: Student ID 236041, FINKI
