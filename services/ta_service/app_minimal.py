# Minimal TA Service for debugging
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

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
    """Get technical analysis for a symbol"""
    return jsonify({
        "symbol": symbol,
        "indicators": {
            "rsi": {"value": 50.0, "overbought": False, "oversold": False},
            "macd": {"bullish": True},
            "test": True
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
