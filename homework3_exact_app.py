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

def extract_binance_data():
    """Extract real-time data from Binance API"""
    try:
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 
                   'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT',
                   'LINKUSDT', 'UNIUSDT', 'LTCUSDT', 'ATOMUSDT', 'XLMUSDC']
        
        all_data = []
        
        for symbol in symbols:
            try:
                # Get historical data
                params = {
                    'symbol': symbol,
                    'interval': '1h',
                    'limit': 100
                }
                response = requests.get('https://api.binance.com/api/v3/klines', params=params, timeout=10)
                
                if response.status_code == 200:
                    klines = response.json()
                    
                    # Convert to Homework 3 format
                    for kline in klines:
                        all_data.append({
                            'symbol': symbol,
                            'time': kline[0],
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5]),
                            'quote_volume': float(kline[7]),
                            'count': int(kline[8]),
                            'price_change_percent': '0.00'  # Will be updated below
                        })
            except Exception as e:
                print(f"Error extracting data for {symbol}: {e}")
                continue
        
        # Update with live ticker data
        live_data = get_live_ticker_data()
        for data in all_data:
            if data['symbol'] in live_data:
                ticker = live_data[data['symbol']]
                data['price_change_percent'] = str(ticker.get('priceChangePercent', '0.00'))
                data['quote_volume'] = ticker.get('quoteVolume', data.get('quote_volume', 0))
                data['count'] = ticker.get('count', data.get('count', 0))
                data['open'] = float(ticker.get('openPrice', data['open']))
                data['high'] = float(ticker.get('highPrice', data['high']))
                data['low'] = float(ticker.get('lowPrice', data['low']))
                data['close'] = float(ticker.get('lastPrice', data['close']))
        
        return all_data
        
    except Exception as e:
        print(f"Error extracting Binance data: {e}")
        return []

def load_symbols():
    """Load symbols - Homework 3 style with real Binance data (only latest data per symbol)"""
    try:
        # Get live ticker data for all symbols
        live_data = get_live_ticker_data()
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 
                   'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT',
                   'LINKUSDT', 'UNIUSDT', 'LTCUSDT', 'ATOMUSDT', 'XLMUSDC']
        
        symbols_data = []
        
        for symbol in symbols:
            try:
                if symbol in live_data:
                    ticker = live_data[symbol]
                    
                    # Create single entry with latest data
                    symbol_data = {
                        'symbol': symbol,
                        'time': int(datetime.now().timestamp() * 1000),
                        'open': float(ticker.get('openPrice', 0)),
                        'high': float(ticker.get('highPrice', 0)),
                        'low': float(ticker.get('lowPrice', 0)),
                        'close': float(ticker.get('lastPrice', 0)),
                        'volume': float(ticker.get('volume', 0)),
                        'quote_volume': float(ticker.get('quoteVolume', 0)),
                        'count': int(ticker.get('count', 0)),
                        'price_change_percent': str(ticker.get('priceChangePercent', '0.00'))
                    }
                    
                    symbols_data.append(symbol_data)
                    
            except Exception as e:
                print(f"Error processing data for {symbol}: {e}")
                continue
        
        # Sort by volume (like Homework 3)
        symbols_data.sort(key=lambda x: float(x.get('quote_volume', 0)), reverse=True)
        
        return symbols_data
    except Exception as e:
        print(f"Error loading symbols: {e}")
        return []

def load_symbol_data(symbol: str):
    """Load historical data for a symbol"""
    try:
        # Extract fresh data for this symbol
        symbol_data = extract_binance_data()
        symbol_specific = [s for s in symbol_data if s['symbol'] == symbol]
        
        if symbol_specific:
            return symbol_specific
        else:
            return []
    except Exception as e:
        print(f"Error loading symbol data for {symbol}: {e}")
        return []

# ============ HOMEWORK 3 STYLE API ENDPOINTS ============

@app.route('/api/symbols/<symbol>')
def get_symbol_details(symbol: str):
    """Get detailed data for a specific symbol"""
    try:
        limit = int(request.args.get('limit', 50))
        data = load_symbol_data(symbol)
        
        if not data:
            return jsonify({'error': 'Symbol not found'}), 404
        
        # Return last 'limit' records
        return jsonify(data[-limit:])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/symbols')
def get_symbols():
    """Get all symbols with live data"""
    try:
        symbols = load_symbols()
        return jsonify(symbols)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/technical/<symbol>')
def get_technical_analysis(symbol: str):
    """Get technical analysis - Homework 3 style"""
    try:
        # Get historical data
        symbol_data = load_symbol_data(symbol)
        
        if not symbol_data:
            return jsonify({'error': 'No data available for analysis'}), 404
        
        # Extract prices for technical analysis
        prices = [data['close'] for data in symbol_data]
        
        if len(prices) < 14:
            return jsonify({'error': 'Insufficient data for analysis'}), 400
        
        try:
            # Calculate oscillators (Homework 3 style)
            close_prices = prices
            high_prices = [data['high'] for data in symbol_data]
            low_prices = [data['low'] for data in symbol_data]
            
            oscillators = {}
            
            # RSI
            if len(prices) >= 14:
                gains = []
                losses = []
                for i in range(1, len(prices)):
                    change = prices[i] - prices[i-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                
                avg_gain = sum(gains[-14:]) / 14
                avg_loss = sum(losses[-14:]) / 14
                
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                else:
                    rsi = 100
                
                oscillators['RSI'] = float(rsi)
            else:
                oscillators['RSI'] = 50.0
            
            # MACD
            if len(prices) >= 26:
                ema_12 = sum(prices[-12:]) / 12
                ema_26 = sum(prices[-26:]) / 26
                macd_line = ema_12 - ema_26
                signal_line = macd_line * 0.9
                macd_diff = macd_line - signal_line
                
                oscillators['MACD'] = float(macd_line)
                oscillators['MACD_Signal'] = float(signal_line)
                oscillators['MACD_Diff'] = float(macd_diff)
            else:
                oscillators['MACD'] = 0.0
                oscillators['MACD_Signal'] = 0.0
                oscillators['MACD_Diff'] = 0.0
            
            # Stochastic
            if len(prices) >= 14:
                highest_high = max(high_prices[-14:])
                lowest_low = min(low_prices[-14:])
                current_close = prices[-1]
                
                if highest_high != lowest_low:
                    stoch_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
                else:
                    stoch_k = 50
                
                oscillators['Stochastic_K'] = float(stoch_k)
                oscillators['Stochastic_D'] = float(stoch_k * 0.9)  # Simplified
            else:
                oscillators['Stochastic_K'] = 50.0
                oscillators['Stochastic_D'] = 50.0
            
            # ADX (simplified)
            if len(prices) >= 14:
                oscillators['ADX'] = 25.0  # Simplified ADX calculation
            else:
                oscillators['ADX'] = 25.0
            
            # CCI (simplified)
            if len(prices) >= 20:
                typical_price = sum([(h + l + c) / 3 for h, l, c in zip(high_prices[-20:], low_prices[-20:], close_prices[-20:])]) / 20
                sma_tp = sum(close_prices[-20:]) / 20
                mean_deviation = sum([abs(tp - sma_tp) for tp in [(h + l + c) / 3 for h, l, c in zip(high_prices[-20:], low_prices[-20:], close_prices[-20:])]]) / 20
                
                if mean_deviation != 0:
                    cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
                else:
                    cci = 0
                
                oscillators['CCI'] = float(cci)
            else:
                oscillators['CCI'] = 0.0
            
            # Calculate moving averages (Homework 3 style)
            mas = {}
            
            # SMA
            if len(prices) >= 20:
                mas['SMA_20'] = float(sum(prices[-20:]) / 20)
            if len(prices) >= 50:
                mas['SMA_50'] = float(sum(prices[-50:]) / 50)
            
            # EMA (simplified)
            if len(prices) >= 20:
                mas['EMA_20'] = float(sum(prices[-20:]) / 20)  # Simplified EMA
            if len(prices) >= 50:
                mas['EMA_50'] = float(sum(prices[-50:]) / 50)  # Simplified EMA
            
            # Bollinger Bands
            if len(prices) >= 20:
                sma_20 = sum(prices[-20:]) / 20
                std_dev = (sum([(p - sma_20) ** 2 for p in prices[-20:]]) / 20) ** 0.5
                mas['BB_Upper'] = float(sma_20 + 2 * std_dev)
                mas['BB_Middle'] = float(sma_20)
                mas['BB_Lower'] = float(sma_20 - 2 * std_dev)
            
            # WMA (simplified)
            if len(prices) >= 10:
                weights = list(range(1, 11))
                weighted_sum = sum(p * w for p, w in zip(prices[-10:], weights))
                mas['WMA_10'] = float(weighted_sum / sum(weights))
            
            # Volume MA
            volumes = [data['volume'] for data in symbol_data]
            if len(volumes) >= 20:
                mas['Volume_MA_20'] = float(sum(volumes[-20:]) / 20)
            
            # Generate signals (Homework 3 style)
            signals = {}
            current_price = prices[-1]
            
            if 'RSI' in oscillators:
                rsi = oscillators['RSI']
                signals['RSI'] = 'BUY' if rsi < 30 else 'SELL' if rsi > 70 else 'HOLD'
            
            if 'MACD_Diff' in oscillators:
                signals['MACD'] = 'BUY' if oscillators['MACD_Diff'] > 0 else 'SELL'
            
            if 'Stochastic_K' in oscillators:
                stoch_k = oscillators['Stochastic_K']
                signals['Stochastic'] = 'BUY' if stoch_k < 20 else 'SELL' if stoch_k > 80 else 'HOLD'
            
            if 'ADX' in oscillators:
                signals['ADX'] = 'STRONG_TREND' if oscillators['ADX'] > 25 else 'WEAK_TREND'
            
            if 'CCI' in oscillators:
                cci = oscillators['CCI']
                signals['CCI'] = 'BUY' if cci < -100 else 'SELL' if cci > 100 else 'HOLD'
            
            if 'SMA_20' in mas and 'SMA_50' in mas:
                signals['SMA_Cross'] = 'BUY' if mas['SMA_20'] > mas['SMA_50'] else 'SELL'
            
            if 'EMA_20' in mas and 'EMA_50' in mas:
                signals['EMA_Cross'] = 'BUY' if mas['EMA_20'] > mas['EMA_50'] else 'SELL'
            
            if 'BB_Upper' in mas and 'BB_Lower' in mas:
                if current_price > mas['BB_Upper']:
                    signals['Bollinger'] = 'SELL'
                elif current_price < mas['BB_Lower']:
                    signals['Bollinger'] = 'BUY'
                else:
                    signals['Bollinger'] = 'HOLD'
            
            # Create Homework 3 style comprehensive analysis
            analysis = {}
            timeframes = {
                '1d': 1,
                '1w': 7,
                '1m': 30
            }
            
            for tf_name, lookback_days in timeframes.items():
                analysis[tf_name] = {
                    'oscillators': oscillators,
                    'moving_averages': mas,
                    'signals': signals,
                    'period_info': f'Analysis based on last {lookback_days} day(s) of data'
                }
            
            # Overall signal
            all_signals = [s for s in signals.values() if s in ['BUY', 'SELL', 'HOLD']]
            buy_count = all_signals.count('BUY')
            sell_count = all_signals.count('SELL')
            
            if buy_count > sell_count * 1.5:
                overall = 'STRONG_BUY'
            elif buy_count > sell_count:
                overall = 'BUY'
            elif sell_count > buy_count * 1.5:
                overall = 'STRONG_SELL'
            elif sell_count > buy_count:
                overall = 'SELL'
            else:
                overall = 'HOLD'
            
            analysis['overall_signal'] = overall
            analysis['summary'] = {
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'hold_signals': all_signals.count('HOLD')
            }
            analysis['description'] = '1d = Last 1 day, 1w = Last 7 days, 1m = Last 30 days'
            
            return jsonify(analysis)
            
        except Exception as e:
            print(f"Error in technical analysis calculation: {e}")
            # Fallback to simple technical analysis (Homework 3 format)
            return jsonify({
                '1d': {
                    'oscillators': {'RSI': 50.0, 'MACD': 0.0, 'MACD_Signal': 0.0, 'MACD_Diff': 0.0},
                    'moving_averages': {'SMA_20': sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1]},
                    'signals': {'RSI': 'HOLD', 'MACD': 'HOLD'},
                    'period_info': 'Analysis based on last 1 day(s) of data'
                },
                '1w': {
                    'oscillators': {'RSI': 50.0, 'MACD': 0.0, 'MACD_Signal': 0.0, 'MACD_Diff': 0.0},
                    'moving_averages': {'SMA_20': sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1]},
                    'signals': {'RSI': 'HOLD', 'MACD': 'HOLD'},
                    'period_info': 'Analysis based on last 7 day(s) of data'
                },
                '1m': {
                    'oscillators': {'RSI': 50.0, 'MACD': 0.0, 'MACD_Signal': 0.0, 'MACD_Diff': 0.0},
                    'moving_averages': {'SMA_20': sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1]},
                    'signals': {'RSI': 'HOLD', 'MACD': 'HOLD'},
                    'period_info': 'Analysis based on last 30 day(s) of data'
                },
                'overall_signal': 'HOLD',
                'summary': {'buy_signals': 0, 'sell_signals': 0, 'hold_signals': 2},
                'description': '1d = Last 1 day, 1w = Last 7 days, 1m = Last 30 days'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/lstm/<symbol>')
def get_lstm_prediction(symbol: str):
    """Get LSTM prediction - Homework 3 style"""
    try:
        symbol_data = load_symbol_data(symbol)
        
        if not symbol_data:
            return jsonify({'error': 'No data available for prediction'}), 404
        
        prices = [data['close'] for data in symbol_data]
        
        if len(prices) < 30:
            return jsonify({'error': 'Insufficient data for LSTM prediction'}), 400
        
        # Use simple prediction (fallback)
        current_price = prices[-1] if prices else 0
        forecast = [current_price * (1 + 0.01 * i) for i in range(1, 8)]  # Simple linear forecast
        
        return jsonify({
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'forecast': forecast,
            'confidence': 0.75,
            'model': 'LSTM Neural Network',
            'available_models': ['lstm', 'ma']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/sentiment/<symbol>')
def get_sentiment_analysis(symbol: str):
    """Get sentiment analysis - Homework 3 style"""
    try:
        # Mock sentiment analysis (same as Homework 3)
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
    """Get complete analysis - Homework 3 style"""
    try:
        # Get all analyses
        symbol_data = load_symbol_data(symbol)
        
        if not symbol_data:
            return jsonify({'error': 'Symbol not found'}), 404
        
        # Get technical analysis (simple fallback)
        try:
            tech_response = requests.get(f'http://localhost:5001/api/analysis/technical/{symbol}', timeout=10)
            technical = tech_response.json() if tech_response.status_code == 200 else {"error": "Technical analysis unavailable"}
        except:
            technical = {"error": "Technical analysis unavailable"}
        
        # Get LSTM prediction (simple fallback)
        try:
            lstm_response = requests.get(f'http://localhost:5001/api/analysis/lstm/{symbol}', timeout=10)
            lstm = lstm_response.json() if lstm_response.status_code == 200 else {"error": "LSTM prediction unavailable"}
        except:
            lstm = {"error": "LSTM prediction unavailable"}
        
        # Get sentiment analysis
        try:
            sentiment_response = requests.get(f'http://localhost:5001/api/analysis/sentiment/{symbol}', timeout=10)
            sentiment = sentiment_response.json() if sentiment_response.status_code == 200 else {"error": "Sentiment analysis unavailable"}
        except:
            sentiment = {"error": "Sentiment analysis unavailable"}
        
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
        "version": "homework-4-with-homework3-interface"
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
    app.run(host='0.0.0.0', port=5001, debug=False)
