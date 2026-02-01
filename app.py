from flask import Flask, jsonify, send_from_directory, request
from pathlib import Path
import json
import requests
import pandas as pd
import sys
import os
from datetime import datetime

app = Flask(__name__)

# ============ HOMEWORK 3 STYLE FUNCTIONS ============

def get_live_ticker_data():
    """Fetch live ticker data from Binance API"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/24hr', timeout=5)
        if response.status_code == 200:
            tickers = response.json()
            return {t['symbol']: t for t in tickers}
        return {}
    except Exception as e:
        print(f"Error fetching ticker data: {e}")
        return {}

def load_symbols():
    """Load symbols from data directory with live ticker data"""
    data_dir = Path('data/cryptocurrencies')
    symbols = []
    live_data = get_live_ticker_data()

    for file in data_dir.glob('*.jsonl'):
        symbol = file.stem
        with open(file, 'r') as f:
            lines = f.readlines()
            if lines:
                last_record = json.loads(lines[-1])
                if symbol in live_data:
                    ticker = live_data[symbol]
                    last_record['price_change_percent'] = ticker.get('priceChangePercent', '0')
                    last_record['quote_volume'] = ticker.get('quoteVolume', last_record.get('quote_volume', '0'))
                    last_record['count'] = ticker.get('count', last_record.get('count', '0'))
                symbols.append(last_record)
    return symbols

def load_symbol_data(symbol: str):
    """Load historical data for a symbol"""
    file_path = Path(f'data/cryptocurrencies/{symbol}.jsonl')
    if not file_path.exists():
        return None
    
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    df = pd.DataFrame(data)
    return df

# ============ HOMEWORK 3 STYLE API ENDPOINTS ============

@app.route('/api/symbols/<symbol>')
def get_symbol_details(symbol: str):
    """Get detailed data for a specific symbol"""
    limit = int(request.args.get('limit', 50))
    file_path = Path(f'data/cryptocurrencies/{symbol}.jsonl')
    if not file_path.exists():
        return jsonify({'error': 'Symbol not found'}), 404

    with open(file_path, 'r') as f:
        lines = f.readlines()
        records = [json.loads(line) for line in lines[-limit:]]
    return jsonify(records)

@app.route('/api/symbols')
def get_symbols():
    """Get all symbols with live data"""
    symbols = load_symbols()
    symbols.sort(key=lambda x: float(x.get('quote_volume', 0)), reverse=True)
    return jsonify(symbols)

@app.route('/api/analysis/technical/<symbol>')
def get_technical_analysis(symbol: str):
    """Get technical analysis - calls microservice"""
    try:
        # Call our microservice
        response = requests.get(f'http://ta-service:5002/api/technical-analysis/{symbol}', timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Technical analysis service unavailable'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/lstm/<symbol>')
def get_lstm_prediction(symbol: str):
    """Get LSTM prediction - calls microservice"""
    try:
        # Call our microservice
        response = requests.get(f'http://prediction-service:5003/api/predict/{symbol}', timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Prediction service unavailable'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/sentiment/<symbol>')
def get_sentiment_analysis(symbol: str):
    """Get sentiment analysis - mock implementation"""
    try:
        # Mock sentiment analysis (same as microservice)
        sentiment_data = {
            "combined_score": 0.65,
            "combined_signal": "NEUTRAL",
            "sentiment_analysis": {
                "sentiment_class": "neutral",
                "average_sentiment": 0.65,
                "news_count": 25
            },
            "onchain_metrics": {
                "active_addresses": 125000,
                "transaction_count": 45000,
                "nvt_ratio": 45.2,
                "mvrv": 1.8
            },
            "onchain_analysis": {
                "signals": ["Moderate activity", "Neutral sentiment"]
            }
        }
        return jsonify(sentiment_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/complete/<symbol>')
def get_complete_analysis(symbol: str):
    """Get complete analysis - combines all analyses"""
    try:
        # Get technical analysis from microservice
        tech_response = requests.get(f'http://ta-service:5002/api/technical-analysis/{symbol}', timeout=10)
        technical = tech_response.json() if tech_response.status_code == 200 else {"error": "Technical analysis unavailable"}
        
        # Get LSTM prediction from microservice
        lstm_response = requests.get(f'http://prediction-service:5003/api/predict/{symbol}', timeout=10)
        lstm = lstm_response.json() if lstm_response.status_code == 200 else {"error": "LSTM prediction unavailable"}
        
        # Mock sentiment analysis
        sentiment = {
            "combined_score": 0.65,
            "combined_signal": "NEUTRAL",
            "sentiment_analysis": {
                "sentiment_class": "neutral",
                "average_sentiment": 0.65,
                "news_count": 25
            },
            "onchain_metrics": {
                "active_addresses": 125000,
                "transaction_count": 45000,
                "nvt_ratio": 45.2,
                "mvrv": 1.8
            },
            "onchain_analysis": {
                "signals": ["Moderate activity", "Neutral sentiment"]
            }
        }
        
        # Generate final recommendation
        final_recommendation = "HOLD"
        
        complete_analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "technical_analysis": technical,
            "lstm_prediction": lstm,
            "sentiment_analysis": sentiment,
            "final_recommendation": final_recommendation,
            "charts": {
                "price": {"labels": [], "datasets": []},
                "technical": {"labels": [], "datasets": []},
                "lstm": {"labels": [], "datasets": []},
                "sentiment_gauge": {"score": 0.65, "label": "NEUTRAL", "color": "#FFA500"},
                "signals_distribution": {"labels": ["BUY", "SELL", "HOLD"], "values": [1, 1, 1], "colors": ["#00FF00", "#FF0000", "#FFA500"]}
            }
        }
        
        return jsonify(complete_analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "CryptoVault Analytics - Homework 3",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "monolithic"
    })

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/')
def index():
    """Serve index.html"""
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
