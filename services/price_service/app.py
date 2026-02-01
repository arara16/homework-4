# Price Data Microservice
# services/price_service/app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from abc import ABC, abstractmethod
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
import time
from typing import Dict, List, Any, Optional

# Import our new pattern implementations
from factory import PriceDataSourceFactory, ConfigurationManager, CacheManager, LoggerManager

app = Flask(__name__)
CORS(app)

# Initialize managers (Singleton Pattern)
config_manager = ConfigurationManager()
cache_manager = CacheManager()
logger_manager = LoggerManager()
logger = logger_manager.get_logger()

# ============ STRATEGY PATTERN IMPLEMENTATION ============

class PriceDataStrategy(ABC):
    """Abstract strategy for fetching price data"""
    
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> list:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        pass


class FileDataStrategy(PriceDataStrategy):
    """Strategy for fetching from JSONL files (local historical data)"""
    
    def __init__(self, file_paths: Dict[str, str]):
        self.file_paths = file_paths  # {"ETHUSDT": "data/ETHUSDT.jsonl", ...}
        self.logger = logger_manager.get_logger()
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch OHLCV data from local files with caching"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {symbol}")
                return cached_data
            
            file_path = self.file_paths.get(symbol)
            if not file_path:
                logger.warning(f"No file path found for symbol: {symbol}")
                return []
            
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    data.append(json.loads(line))
            
            # Return most recent candles
            data = data[-limit:] if len(data) > limit else data
            
            # Cache the result
            cache_manager.set(cache_key, data, ttl_seconds=300)  # 5 minutes cache
            
            response_time = time.time() - start_time
            logger_manager.log_request(f"fetch_ohlcv_file", {"symbol": symbol, "limit": limit}, response_time)
            
            return data
            
        except Exception as e:
            logger_manager.log_error(e, f"FileDataStrategy.fetch_ohlcv for {symbol}")
            return []
    
    def is_available(self) -> bool:
        return True
    
    def get_source_name(self) -> str:
        return "File (Historical)"


class APIDataStrategy(PriceDataStrategy):
    """Strategy for fetching from external APIs (simulated)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> list:
        # In production, this would call Binance/CoinGecko API
        # For now, generate synthetic data based on historical pattern
        return self._generate_synthetic_data(symbol, limit)
    
    def _generate_synthetic_data(self, symbol: str, limit: int):
        """Generate realistic synthetic OHLCV data"""
        data = []
        base_price = 2500 if symbol == "ETHUSDT" else 50000
        
        for i in range(limit):
            timestamp = int((datetime.now() - timedelta(hours=limit-i)).timestamp() * 1000)
            change = np.random.normal(0, 100)
            
            data.append({
                "time": timestamp,
                "open": base_price + change,
                "high": base_price + change + np.random.uniform(0, 200),
                "low": base_price + change - np.random.uniform(0, 200),
                "close": base_price + change,
                "volume": np.random.uniform(10, 1000)
            })
        
        return data
    
    def is_available(self) -> bool:
        return True
    
    def get_source_name(self) -> str:
        return "Live API"


class CacheStrategy(PriceDataStrategy):
    """Strategy for fetching from in-memory cache"""
    
    def __init__(self):
        self.cache = {}
    
    def set(self, symbol: str, data: list):
        self.cache[symbol] = data
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> list:
        return self.cache.get(symbol, [])
    
    def is_available(self) -> bool:
        return len(self.cache) > 0
    
    def get_source_name(self) -> str:
        return "Cache"


class PriceDataManager:
    """Context class that manages price data strategies"""
    
    def __init__(self):
        self.strategies = []
        self.current_strategy = None
    
    def add_strategy(self, strategy: PriceDataStrategy):
        self.strategies.append(strategy)
    
    def set_primary_strategy(self, strategy: PriceDataStrategy):
        self.current_strategy = strategy
    
    def get_price_data(self, symbol: str, timeframe: str, limit: int = 100):
        """Try strategies in fallback order"""
        
        # If primary strategy is set and available, use it
        if self.current_strategy and self.current_strategy.is_available():
            data = self.current_strategy.fetch_ohlcv(symbol, timeframe, limit)
            if data:
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "data": data,
                    "source": self.current_strategy.get_source_name(),
                    "count": len(data)
                }
        
        # Fallback: try other strategies
        for strategy in self.strategies:
            if strategy.is_available():
                data = strategy.fetch_ohlcv(symbol, timeframe, limit)
                if data:
                    return {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "data": data,
                        "source": strategy.get_source_name(),
                        "count": len(data)
                    }
        
        return {"error": "No data available", "symbol": symbol}


# ============ INITIALIZATION ============

# Import data file paths
DATA_FILES = {
    "ETHUSDT": "data/ETHUSDT.jsonl",
    "XLMUSDC": "data/XLMUSDC.jsonl",
    "LINKUSDC": "data/LINKUSDC.jsonl"
}

# ============ SERVICE INITIALIZATION WITH FACTORY PATTERN ============

# Register strategies with factory
PriceDataSourceFactory.register_source('file', FileDataStrategy)
PriceDataSourceFactory.register_source('api', APIDataStrategy)

# Initialize strategies using configuration
file_strategy = PriceDataSourceFactory.create_source('file', DATA_FILES)
api_strategy = PriceDataSourceFactory.create_source('api', {})

# Create manager with strategies
manager = PriceDataManager()
manager.add_strategy(file_strategy)
manager.add_strategy(api_strategy)
manager.set_primary_strategy(file_strategy)  # Use file as primary for demo

logger.info("Price Data Service initialized with strategies")


# ============ API ENDPOINTS ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "Price Data Service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/prices/<symbol>', methods=['GET'])
def get_prices(symbol):
    """Get OHLCV data for a symbol"""
    
    timeframe = request.args.get('timeframe', '1h')
    limit = int(request.args.get('limit', 100))
    
    result = manager.get_price_data(symbol, timeframe, limit)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result)


@app.route('/api/prices/latest/<symbol>', methods=['GET'])
def get_latest_price(symbol):
    """Get the latest price for a symbol"""
    
    result = manager.get_price_data(symbol, "1m", 1)
    
    if "error" in result:
        return jsonify(result), 404
    
    if result["data"]:
        latest = result["data"][-1]
        return jsonify({
            "symbol": symbol,
            "price": latest.get("close", 0),
            "timestamp": latest.get("time", 0),
            "source": result["source"]
        })
    
    return jsonify({"error": "No data available"}), 404


@app.route('/api/prices/batch', methods=['POST'])
def get_batch_prices():
    """Get prices for multiple symbols"""
    
    symbols = request.json.get("symbols", [])
    limit = request.json.get("limit", 50)
    
    result = {}
    for symbol in symbols:
        result[symbol] = manager.get_price_data(symbol, "1h", limit)
    
    return jsonify(result)


@app.route('/api/prices/stats/<symbol>', methods=['GET'])
def get_price_stats(symbol):
    """Get price statistics (high, low, change, etc.)"""
    
    result = manager.get_price_data(symbol, "1d", 30)
    
    if "error" in result:
        return jsonify(result), 404
    
    data = result["data"]
    closes = [d.get("close", 0) for d in data]
    
    if not closes:
        return jsonify({"error": "No data"}), 404
    
    return jsonify({
        "symbol": symbol,
        "current_price": closes[-1],
        "high": max(closes),
        "low": min(closes),
        "avg": sum(closes) / len(closes),
        "change": ((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] else 0,
        "count": len(closes),
        "source": result["source"]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)