-- CryptoVault Database Initialization Script
-- init_db.sql

-- Create tables for cryptocurrency data storage

-- Prices table - stores OHLCV data
CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp BIGINT NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, timestamp),
    INDEX idx_symbol_time (symbol, timestamp DESC)
);

-- Technical Analysis Results table
CREATE TABLE IF NOT EXISTS technical_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp BIGINT NOT NULL,
    rsi DECIMAL(10, 4),
    macd_line DECIMAL(20, 8),
    macd_signal DECIMAL(20, 8),
    macd_histogram DECIMAL(20, 8),
    bb_upper DECIMAL(20, 8),
    bb_middle DECIMAL(20, 8),
    bb_lower DECIMAL(20, 8),
    sma_short DECIMAL(20, 8),
    sma_long DECIMAL(20, 8),
    trend VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp),
    INDEX idx_symbol_time (symbol, timestamp DESC)
);

-- Predictions table - stores model predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    forecast_day INT NOT NULL,
    predicted_price DECIMAL(20, 8) NOT NULL,
    confidence DECIMAL(5, 4),
    prediction_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_model (symbol, model_name, created_at DESC)
);

-- Trading Signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal VARCHAR(20) NOT NULL,
    strength DECIMAL(5, 4),
    price_at_signal DECIMAL(20, 8),
    indicators_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_created (symbol, created_at DESC)
);

-- Users table - for future user authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Watchlist table - for user watchlists
CREATE TABLE IF NOT EXISTS watchlists (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, symbol)
);

-- Alerts table - for price alerts
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price_level DECIMAL(20, 8),
    alert_type VARCHAR(50),
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_symbol (user_id, symbol)
);

-- Portfolio table - for tracking investments
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(20, 8),
    avg_purchase_price DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_symbol (user_id, symbol)
);

-- Service Health logs
CREATE TABLE IF NOT EXISTS service_health_logs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20),
    response_time_ms INT,
    error_message TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_service_logged (service_name, logged_at DESC)
);

-- Insert sample crypto symbols
INSERT IGNORE INTO prices (symbol, timeframe, timestamp, open, high, low, close, volume)
VALUES 
    ('ETHUSDT', '1h', UNIX_TIMESTAMP() * 1000, 2500.00, 2510.00, 2490.00, 2505.00, 150.50),
    ('BTCUSDT', '1h', UNIX_TIMESTAMP() * 1000, 50000.00, 50500.00, 49500.00, 50250.00, 25.75),
    ('XLMUSDC', '1h', UNIX_TIMESTAMP() * 1000, 0.50, 0.51, 0.49, 0.50, 5000.00),
    ('LINKUSDC', '1h', UNIX_TIMESTAMP() * 1000, 25.00, 25.50, 24.50, 25.25, 500.00);

-- Create views for common queries

-- View for latest prices per symbol
CREATE OR REPLACE VIEW latest_prices AS
SELECT 
    symbol,
    close,
    timestamp,
    ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
FROM prices
WHERE rn = 1;

-- View for price statistics
CREATE OR REPLACE VIEW price_statistics AS
SELECT 
    symbol,
    MIN(low) as min_price,
    MAX(high) as max_price,
    AVG(close) as avg_price,
    STDDEV(close) as price_volatility,
    COUNT(*) as candle_count
FROM prices
GROUP BY symbol;

-- Grants for application user (adjust as needed)
GRANT SELECT, INSERT, UPDATE ON cryptovault_db.* TO 'cryptovault'@'%';
FLUSH PRIVILEGES;
