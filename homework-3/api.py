from flask import Flask, jsonify, send_from_directory, request
from pathlib import Path
import json
import requests
import pandas as pd
import sys
sys.path.append(str(Path(__file__).parent))

from analysis.technical_analysis import TechnicalAnalyzer
from analysis.lstm_prediction import LSTMPredictor
from analysis.sentiment_analysis import CombinedAnalyzer
from analysis.chart_generator import ChartGenerator

app = Flask(__name__)

def get_live_ticker_data():
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/24hr')
        if response.status_code == 200:
            tickers = response.json()
            return {t['symbol']: t for t in tickers}
        return {}
    except Exception as e:
        print(f"Error fetching ticker data: {e}")
        return {}

def load_symbols():
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

def load_symbol_data(symbol: str) -> pd.DataFrame:
    file_path = Path(f'data/cryptocurrencies/{symbol}.jsonl')
    if not file_path.exists():
        return None
    
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    df = pd.DataFrame(data)
    return df

@app.route('/api/symbols/<symbol>')
def get_symbol_details(symbol: str):
    limit = 50
    file_path = Path(f'data/cryptocurrencies/{symbol}.jsonl')
    if not file_path.exists():
        return jsonify({'error': 'Symbol not found'}), 404

    with open(file_path, 'r') as f:
        lines = f.readlines()
        records = [json.loads(line) for line in lines[-limit:]]
    return jsonify(records)

@app.route('/api/symbols')
def get_symbols():
    symbols = load_symbols()
    symbols.sort(key=lambda x: float(x.get('quote_volume', 0)), reverse=True)
    return jsonify(symbols)

@app.route('/api/analysis/technical/<symbol>')
def get_technical_analysis(symbol: str):
    try:
        df = load_symbol_data(symbol)
        if df is None or len(df) < 50:
            return jsonify({'error': 'Insufficient data for analysis'}), 400
        
        analyzer = TechnicalAnalyzer(df)
        analysis = analyzer.get_comprehensive_analysis()
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/lstm/<symbol>')
def get_lstm_prediction(symbol: str):
    try:
        df = load_symbol_data(symbol)
        if df is None or len(df) < 100:
            return jsonify({'error': 'Insufficient data for LSTM training'}), 400
        
        predictor = LSTMPredictor(df, lookback_period=30)
        predictions = predictor.get_comprehensive_prediction()
        
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/sentiment/<symbol>')
def get_sentiment_analysis(symbol: str):
    try:
        analyzer = CombinedAnalyzer(symbol)
        analysis = analyzer.get_comprehensive_analysis()
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/complete/<symbol>')
def get_complete_analysis(symbol: str):
    try:
        df = load_symbol_data(symbol)
        if df is None or len(df) < 100:
            return jsonify({'error': 'Insufficient data'}), 400
        
        tech_analyzer = TechnicalAnalyzer(df)
        technical = tech_analyzer.get_comprehensive_analysis()
        
        lstm_predictor = LSTMPredictor(df, lookback_period=30)
        lstm = lstm_predictor.get_comprehensive_prediction()
        
        sent_analyzer = CombinedAnalyzer(symbol)
        sentiment = sent_analyzer.get_comprehensive_analysis()
        
        # Generate charts
        chart_gen = ChartGenerator()
        price_chart = chart_gen.generate_price_chart(df)
        technical_chart = chart_gen.generate_technical_indicators_chart(df, technical)
        
        lstm_chart = chart_gen.generate_lstm_prediction_chart(
            historical_data=df['close'].tolist(),
            predictions=lstm['future_predictions']['predictions'],
            dates=df['date'].tolist(),
            future_dates=lstm['future_predictions']['dates']
        )
        
        sentiment_gauge = chart_gen.generate_sentiment_gauge(
            sentiment['combined_score']
        )
        
        signals_dist = chart_gen.generate_signals_distribution(
            technical['1d']['signals']
        )
        
        signals = [
            technical['overall_signal'],
            sentiment['combined_signal']
        ]
        
        buy_count = sum(1 for s in signals if 'BUY' in s)
        sell_count = sum(1 for s in signals if 'SELL' in s)
        
        if buy_count > sell_count:
            final_recommendation = 'BUY'
        elif sell_count > buy_count:
            final_recommendation = 'SELL'
        else:
            final_recommendation = 'HOLD'
        
        return jsonify({
            'symbol': symbol,
            'timestamp': pd.Timestamp.now().isoformat(),
            'technical_analysis': technical,
            'lstm_prediction': lstm,
            'sentiment_analysis': sentiment,
            'final_recommendation': final_recommendation,
            'charts': {
                'price': price_chart,
                'technical': technical_chart,
                'lstm': lstm_chart,
                'sentiment_gauge': sentiment_gauge,
                'signals_distribution': signals_dist
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
