from flask import Flask, jsonify, send_from_directory
import requests
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/health')
def health():
    return jsonify({
        'service': 'CryptoVault Analytics - Azure Cloud',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/symbols')
def get_symbols():
    try:
        # Get live data from Binance
        response = requests.get('https://api.binance.com/api/v3/ticker/24hr', timeout=5)
        if response.status_code == 200:
            tickers = response.json()
            # Get top 15 by volume
            top_tickers = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)[:15]
            
            symbols = []
            for ticker in top_tickers:
                if ticker['symbol'].endswith('USDT'):
                    symbols.append({
                        'symbol': ticker['symbol'],
                        'close': float(ticker['lastPrice']),
                        'open': float(ticker['openPrice']),
                        'high': float(ticker['highPrice']),
                        'low': float(ticker['lowPrice']),
                        'volume': float(ticker['volume']),
                        'quote_volume': float(ticker['quoteVolume']),
                        'count': int(ticker['count']),
                        'number_of_trades': int(ticker['count']),
                        'price_change_percent': ticker['priceChangePercent'],
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'timestamp': int(datetime.now().timestamp())
                    })
            return jsonify(symbols)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/complete/<symbol>')
def get_analysis(symbol):
    try:
        # Mock analysis data
        return jsonify({
            'symbol': symbol,
            'current_price': 50000,
            'price_change_percent': '2.5',
            'technical_analysis': {
                '1d': {
                    'oscillators': {
                        'rsi': {'value': 65, 'signal': 'NEUTRAL'},
                        'stochastic': {'k': 70, 'd': 65, 'signal': 'BUY'}
                    },
                    'moving_averages': {
                        'sma_20': {'value': 49500, 'signal': 'BUY'},
                        'sma_50': {'value': 48000, 'signal': 'BUY'}
                    },
                    'signals': {
                        'overall_signal': 'BUY',
                        'summary': {'buy': 3, 'sell': 0, 'hold': 2}
                    }
                }
            },
            'lstm_prediction': {
                '7d': {
                    'predictions': [51000, 52000, 51500, 52500, 53000, 53500, 54000],
                    'confidence': 85
                }
            },
            'sentiment_analysis': {
                'sentiment': 'BULLISH',
                'score': 0.75,
                'confidence': 80
            },
            'final_recommendation': {
                'signal': 'BUY',
                'confidence': 85,
                'reasoning': 'Strong technical and sentiment indicators'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(__import__('os').environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
