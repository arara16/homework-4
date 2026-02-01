# Technical Analysis Microservice
# services/ta_service/app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime
import json


class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types"""
    
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.float64) or isinstance(obj, np.float32):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json = NumpyJSONEncoder
CORS(app)

# ============ STRATEGY PATTERN FOR TA INDICATORS ============

class TAStrategy(ABC):
    """Abstract strategy for technical analysis calculations"""
    
    @abstractmethod
    def calculate(self, prices: list) -> dict:
        pass
    
    @abstractmethod
    def get_indicator_name(self) -> str:
        pass


class RSIStrategy(TAStrategy):
    """Relative Strength Index calculation"""
    
    def calculate(self, prices: list, period: int = 14) -> dict:
        if len(prices) < period + 1:
            return {"error": "Insufficient data"}
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs else 0
        
        return {
            "indicator": "RSI",
            "value": float(rsi),
            "overbought": bool(rsi > 70),
            "oversold": bool(rsi < 30),
            "period": int(period)
        }
    
    def get_indicator_name(self) -> str:
        return "RSI"


class MACDStrategy(TAStrategy):
    """MACD (Moving Average Convergence Divergence) calculation"""
    
    def calculate(self, prices: list) -> dict:
        if len(prices) < 26:
            return {"error": "Insufficient data"}
        
        prices = np.array(prices)
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        
        macd_line = ema12 - ema26
        signal_line = self._calculate_ema(macd_line, 9)
        histogram = macd_line - signal_line
        
        return {
            "indicator": "MACD",
            "macd_line": float(macd_line[-1]),
            "signal_line": float(signal_line[-1]),
            "histogram": float(histogram[-1]),
            "bullish": bool(histogram[-1] > 0)
        }
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(prices))
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def get_indicator_name(self) -> str:
        return "MACD"


class BollingerBandsStrategy(TAStrategy):
    """Bollinger Bands calculation"""
    
    def calculate(self, prices: list, period: int = 20, std_dev: float = 2.0) -> dict:
        if len(prices) < period:
            return {"error": "Insufficient data"}
        
        prices = np.array(prices[-period:])
        sma = np.mean(prices)
        std = np.std(prices)
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = prices[-1]
        
        return {
            "indicator": "Bollinger Bands",
            "middle_band": float(sma),
            "upper_band": float(upper_band),
            "lower_band": float(lower_band),
            "bandwidth": float(upper_band - lower_band),
            "current_price": float(current_price),
            "position": "overbought" if current_price > upper_band else "oversold" if current_price < lower_band else "neutral"
        }
    
    def get_indicator_name(self) -> str:
        return "Bollinger Bands"


class MovingAverageStrategy(TAStrategy):
    """Simple and Exponential Moving Averages"""
    
    def calculate(self, prices: list, period_short: int = 20, period_long: int = 50) -> dict:
        prices = np.array(prices)
        
        if len(prices) < period_long:
            return {"error": "Insufficient data"}
        
        sma_short = np.mean(prices[-period_short:])
        sma_long = np.mean(prices[-period_long:])
        
        return {
            "indicator": "Moving Averages",
            "sma_short": float(sma_short),
            "sma_long": float(sma_long),
            "trend": "bullish" if sma_short > sma_long else "bearish",
            "crossover": "golden" if sma_short > sma_long else "death"
        }
    
    def get_indicator_name(self) -> str:
        return "Moving Averages"


class TACalculator:
    """Context class for technical analysis strategies"""
    
    def __init__(self):
        self.strategies = {
            "rsi": RSIStrategy(),
            "macd": MACDStrategy(),
            "bb": BollingerBandsStrategy(),
            "ma": MovingAverageStrategy()
        }
    
    def calculate_all(self, prices: list) -> dict:
        """Calculate all technical indicators"""
        
        results = {
            "rsi": self.strategies["rsi"].calculate(prices),
            "macd": self.strategies["macd"].calculate(prices),
            "bb": self.strategies["bb"].calculate(prices),
            "ma": self.strategies["ma"].calculate(prices),
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure all boolean values are Python bool, not numpy bool_
        return self._convert_numpy_types(results)
    
    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to Python types"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.float64) or isinstance(obj, np.float32):
            return float(obj)
        else:
            return obj
    
    def calculate(self, indicator: str, prices: list) -> dict:
        """Calculate specific indicator"""
        
        if indicator not in self.strategies:
            return {"error": f"Unknown indicator: {indicator}"}
        
        result = self.strategies[indicator].calculate(prices)
        return self._convert_numpy_types(result)


# ============ INITIALIZATION ============

calculator = TACalculator()
PRICE_SERVICE_URL = "http://price-service:5001"


# ============ API ENDPOINTS ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "Technical Analysis Service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/technical-analysis/<symbol>', methods=['GET'])
def get_technical_analysis(symbol):
    """Get all technical analysis indicators for a symbol"""
    
    try:
        # Fetch price data from price service
        response = requests.get(
            f"{PRICE_SERVICE_URL}/api/prices/{symbol}",
            timeout=5
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch price data"}), 502
        
        price_data = response.json()
        prices = [candle.get("close", 0) for candle in price_data.get("data", [])]
        
        if not prices:
            return jsonify({"error": "No price data available"}), 404
        
        # Calculate all indicators
        ta_results = calculator.calculate_all(prices)
        
        return jsonify({
            "symbol": symbol,
            "indicators": ta_results,
            "analysis_timestamp": datetime.now().isoformat(),
            "price_count": len(prices)
        })
    
    except requests.RequestException as e:
        return jsonify({"error": f"Service communication error: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/technical-analysis/<symbol>/<indicator>', methods=['GET'])
def get_indicator(symbol, indicator):
    """Get specific technical indicator"""
    
    try:
        response = requests.get(
            f"{PRICE_SERVICE_URL}/api/prices/{symbol}",
            timeout=5
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch price data"}), 502
        
        price_data = response.json()
        prices = [candle.get("close", 0) for candle in price_data.get("data", [])]
        
        if not prices:
            return jsonify({"error": "No price data available"}), 404
        
        result = calculator.calculate(indicator, prices)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "symbol": symbol,
            "indicator": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/technical-analysis/batch', methods=['POST'])
def get_batch_analysis():
    """Get technical analysis for multiple symbols"""
    
    symbols = request.json.get("symbols", [])
    indicators = request.json.get("indicators", ["rsi", "macd", "bb", "ma"])
    
    results = {}
    
    for symbol in symbols:
        try:
            response = requests.get(
                f"{PRICE_SERVICE_URL}/api/prices/{symbol}",
                timeout=5
            )
            
            if response.status_code == 200:
                price_data = response.json()
                prices = [c.get("close", 0) for c in price_data.get("data", [])]
                
                results[symbol] = {
                    "indicators": {
                        ind: calculator.calculate(ind, prices)
                        for ind in indicators
                    }
                }
            else:
                results[symbol] = {"error": f"Failed to fetch price data (HTTP {response.status_code})"}
        except requests.RequestException as e:
            results[symbol] = {"error": f"Service communication error: {str(e)}"}
        except Exception as e:
            results[symbol] = {"error": f"Analysis failed: {str(e)}"}
    
    return jsonify(results)


@app.route('/api/signal/<symbol>', methods=['GET'])
def get_trading_signal(symbol):
    """Get automated trading signal based on multiple indicators"""
    
    try:
        response = requests.get(
            f"{PRICE_SERVICE_URL}/api/prices/{symbol}",
            timeout=5
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data"}), 502
        
        price_data = response.json()
        prices = [c.get("close", 0) for c in price_data.get("data", [])]
        
        # Calculate indicators
        rsi_result = calculator.calculate("rsi", prices)
        macd_result = calculator.calculate("macd", prices)
        ma_result = calculator.calculate("ma", prices)
        
        # Generate signal
        signal_score = 0
        
        if not rsi_result.get("error"):
            if rsi_result["oversold"]:
                signal_score += 1
            if rsi_result["overbought"]:
                signal_score -= 1
        
        if not macd_result.get("error") and macd_result.get("bullish"):
            signal_score += 1
        
        if not ma_result.get("error") and ma_result.get("trend") == "bullish":
            signal_score += 1
        
        # Determine signal
        if signal_score >= 2:
            signal = "BUY"
            confidence = min(signal_score / 3, 1.0)
        elif signal_score <= -2:
            signal = "SELL"
            confidence = min(abs(signal_score) / 3, 1.0)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return jsonify({
            "symbol": symbol,
            "signal": signal,
            "confidence": float(confidence),
            "score": signal_score,
            "indicators": {
                "rsi": rsi_result,
                "macd": macd_result,
                "ma": ma_result
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)