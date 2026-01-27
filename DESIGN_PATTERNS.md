# Design Patterns Implementation - Homework 4

## Pattern Used: Strategy Pattern

### 1. Pattern Definition
The Strategy Pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable.

### 2. Implementation Locations

#### Price Service (services/price_service/app.py)
**Strategies**: FileDataStrategy, APIDataStrategy, CacheStrategy
**Purpose**: Multiple data sources with fallback mechanism
**Benefits**: Flexibility, resilience, testability

#### Technical Analysis Service (services/ta_service/app.py)
**Strategies**: RSI, MACD, Bollinger Bands, Moving Averages (5 oscillators + 5 MAs)
**Purpose**: Various technical indicator calculations
**Benefits**: Modular indicator system, easy to add new indicators

#### Prediction Service (services/prediction_service/app.py)
**Strategies**: LSTMPredictionStrategy, MovingAveragePredictionStrategy
**Purpose**: Multiple forecasting models
**Benefits**: Model flexibility, graceful degradation

### 3. Why Strategy Pattern?

**Advantages**:
1. **Flexibility** - Easy to add new data sources, indicators, or prediction methods
2. **Maintainability** - Each strategy is independent and testable
3. **Extensibility** - New strategies can be added without modifying existing code
4. **Runtime Selection** - Strategies selected at runtime based on availability
5. **Reusability** - Strategies can be reused across different services
6. **Decoupling** - Business logic decoupled from algorithm implementation

### 4. Class Diagram Structure

Price Service Pattern:
- PriceDataStrategy (abstract)
  - FileDataStrategy
  - APIDataStrategy
  - CacheStrategy
  - PriceDataManager (context)

### 5. Benefits for Microservices

- **Price Service**: Cache → File → API fallback
- **TA Service**: Multiple independent indicators
- **Prediction Service**: LSTM → Moving Average fallback

See services code for detailed implementation.
