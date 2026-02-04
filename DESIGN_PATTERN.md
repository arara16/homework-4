# Homework 4: Design Pattern Implementation - Strategy Pattern

## Executive Summary

This document details the implementation of the **Strategy Pattern** in the CryptoVault Microservices Architecture as part of Homework 4 for Software Design and Architecture.

---

## 1. Overview of Strategy Pattern

### Definition
The Strategy Pattern is a behavioral design pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

### Why Strategy Pattern?
- **Flexibility**: Easily switch between different data sources (APIs, databases, files)
- **Scalability**: Add new data sources without modifying existing code
- **Maintainability**: Each strategy is independent and testable
- **Reusability**: Strategies can be used across multiple components

---

## 2. Implementation in CryptoVault

### 2.1 Problem Statement

The CryptoVault application needs to fetch cryptocurrency data from multiple sources:
- **Real-time API** (Binance, CoinGecko)
- **Local Database** (PostgreSQL, MongoDB)
- **Cache Layer** (Redis)
- **CSV Files** (Historical data)

Without the Strategy Pattern, we'd have:
```python
# ❌ BAD: Hard-coded dependencies
if source == "binance":
    data = fetch_from_binance()
elif source == "database":
    data = fetch_from_database()
elif source == "cache":
    data = fetch_from_cache()
```

### 2.2 Solution: Strategy Pattern Implementation

#### **Step 1: Define the Strategy Interface**

```python
from abc import ABC, abstractmethod

class DataSourceStrategy(ABC):
    """Abstract base class defining the contract for all data sources"""
    
    @abstractmethod
    def fetch_price_data(self, symbol: str, timeframe: str) -> dict:
        """Fetch price data for a given symbol"""
        pass
    
    @abstractmethod
    def fetch_technical_analysis(self, symbol: str) -> dict:
        """Fetch technical analysis indicators"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the data source is available"""
        pass
```

#### **Step 2: Implement Concrete Strategies**

```python
class BinanceStrategy(DataSourceStrategy):
    """Strategy for fetching data from Binance API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.binance.com/api/v3"
    
    def fetch_price_data(self, symbol: str, timeframe: str) -> dict:
        """Fetch OHLCV data from Binance"""
        # Implementation details
        pass
    
    def fetch_technical_analysis(self, symbol: str) -> dict:
        """Fetch TA indicators from Binance"""
        pass
    
    def is_available(self) -> bool:
        """Check API connectivity"""
        pass

class DatabaseStrategy(DataSourceStrategy):
    """Strategy for fetching data from local PostgreSQL database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def fetch_price_data(self, symbol: str, timeframe: str) -> dict:
        """Query historical data from database"""
        pass
    
    def fetch_technical_analysis(self, symbol: str) -> dict:
        """Query pre-computed indicators from database"""
        pass
    
    def is_available(self) -> bool:
        """Check database connection"""
        pass

class CacheStrategy(DataSourceStrategy):
    """Strategy for fetching data from Redis cache"""
    
    def __init__(self, redis_client):
        self.cache = redis_client
    
    def fetch_price_data(self, symbol: str, timeframe: str) -> dict:
        """Get cached price data"""
        pass
    
    def fetch_technical_analysis(self, symbol: str) -> dict:
        """Get cached indicators"""
        pass
    
    def is_available(self) -> bool:
        """Check cache availability"""
        pass
```

#### **Step 3: Create the Context Class**

```python
class DataManager:
    """Context class that uses the strategy to fetch data"""
    
    def __init__(self, strategy: DataSourceStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: DataSourceStrategy):
        """Switch to a different data source strategy"""
        self._strategy = strategy
    
    def get_price_data(self, symbol: str, timeframe: str) -> dict:
        """Delegate to current strategy"""
        if not self._strategy.is_available():
            raise Exception(f"Strategy {self._strategy.__class__.__name__} is unavailable")
        return self._strategy.fetch_price_data(symbol, timeframe)
    
    def get_technical_analysis(self, symbol: str) -> dict:
        """Delegate to current strategy"""
        return self._strategy.fetch_technical_analysis(symbol)
```

#### **Step 4: Usage in API Endpoints**

```python
from flask import Flask, request
from strategy_pattern import (
    DataManager, 
    BinanceStrategy, 
    DatabaseStrategy,
    CacheStrategy
)

app = Flask(__name__)

# Initialize strategies
binance_strategy = BinanceStrategy(api_key="YOUR_API_KEY")
db_strategy = DatabaseStrategy(db_connection=db)
cache_strategy = CacheStrategy(redis_client=redis)

# Create data manager with default strategy
data_manager = DataManager(cache_strategy)

@app.route('/api/crypto/price/<symbol>')
def get_price(symbol):
    """Get price data, trying strategies in order: cache -> database -> API"""
    
    strategies = [cache_strategy, db_strategy, binance_strategy]
    
    for strategy in strategies:
        try:
            if strategy.is_available():
                data_manager.set_strategy(strategy)
                price_data = data_manager.get_price_data(symbol, "1d")
                return {"data": price_data, "source": strategy.__class__.__name__}
        except Exception as e:
            continue
    
    return {"error": "No available data source"}, 503

@app.route('/api/crypto/ta/<symbol>')
def get_ta(symbol):
    """Get technical analysis from best available source"""
    data_manager.set_strategy(db_strategy)  # Database has pre-computed indicators
    ta_data = data_manager.get_technical_analysis(symbol)
    return {"data": ta_data}
```

---

## 3. Benefits Realized

| Benefit | Example |
|---------|---------|
| **Flexibility** | Switch from Binance API to database query with one line: `data_manager.set_strategy(db_strategy)` |
| **Testability** | Easy to mock strategies for unit testing |
| **Open/Closed** | Open for extension (new strategies) but closed for modification |
| **Single Responsibility** | Each strategy handles one data source |
| **Fallback Logic** | Try cache first, then database, then API |

---

## 4. Architectural Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     API Endpoints                            │
│         (Price, Technical Analysis, Prediction)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              DataManager (Context)                           │
│  - set_strategy(strategy)                                    │
│  - get_price_data(symbol, timeframe)                        │
│  - get_technical_analysis(symbol)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌─────────┐
   │ Cache   │   │Database  │   │ Binance │
   │Strategy │   │Strategy  │   │Strategy │
   └─────────┘   └──────────┘   └─────────┘
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌─────────┐
   │  Redis  │   │PostgreSQL│   │API Call │
   └─────────┘   └──────────┘   └─────────┘
```

---

## 5. Design Principles Applied

### 5.1 SOLID Principles

- **S**ingle Responsibility: Each strategy handles one data source
- **O**pen/Closed: Open for new strategies, closed for modification
- **L**iskov Substitution: All strategies are interchangeable
- **I**nterface Segregation: Clean DataSourceStrategy interface
- **D**ependency Inversion: Depend on abstractions, not concrete classes

### 5.2 Key Design Improvements

1. **Reduce Coupling**: Components depend on the strategy interface, not implementations
2. **Increase Cohesion**: Related data-fetching logic grouped in strategies
3. **Enable Testing**: Mock strategies for unit tests
4. **Support Fallback**: Try multiple strategies automatically

---

## 6. Integration with Microservices

### Microservice Structure
```
CryptoVault Microservices
│
├── API Gateway (Spring Boot)
│   └── Routes requests to appropriate services
│
├── Price Data Service (Python Flask)
│   └── Uses Strategy Pattern for: API, Database, Cache
│
├── Technical Analysis Service (Python Flask)
│   └── Uses Strategy Pattern for: Cached indicators, Real-time calculation
│
├── LSTM Prediction Service (Python Flask)
│   └── Uses Strategy Pattern for: Model versions, Data sources
│
└── Shared Infrastructure
    ├── PostgreSQL (Primary data store)
    ├── Redis (Cache layer)
    └── Message Queue (Service communication)
```

Each microservice uses the Strategy Pattern independently, making them loosely coupled and highly maintainable.

---

## 7. Testing Strategy

```python
# ✅ Easy to test with mock strategies

class MockDataStrategy(DataSourceStrategy):
    def fetch_price_data(self, symbol: str, timeframe: str) -> dict:
        return {"symbol": symbol, "price": 50000, "timestamp": 1234567890}
    
    def fetch_technical_analysis(self, symbol: str) -> dict:
        return {"rsi": 65, "macd": 150}
    
    def is_available(self) -> bool:
        return True

# Test API with mock data
def test_get_price():
    data_manager = DataManager(MockDataStrategy())
    price_data = data_manager.get_price_data("BTCUSDT", "1d")
    assert price_data["price"] == 50000
```

---

## 8. Conclusion

The Strategy Pattern has been successfully implemented in CryptoVault to provide:
- **Flexibility** in choosing data sources
- **Scalability** for adding new sources
- **Maintainability** through clear separation of concerns
- **Testability** with easy mocking capabilities
- **Resilience** through fallback mechanisms

This design pattern is fundamental to the microservices architecture and enables each service to independently manage its data sources while maintaining clean, testable, and maintainable code.

---

## 9. References

- Gamma et al. "Design Patterns: Elements of Reusable Object-Oriented Software" (1994)
- Refactoring.Guru: https://refactoring.guru/design-patterns/strategy
- SOLID Principles: https://en.wikipedia.org/wiki/SOLID

---

**Document Version**: 1.0  
**Date**: January 2026  
**Author**: CryptoVault Development Team