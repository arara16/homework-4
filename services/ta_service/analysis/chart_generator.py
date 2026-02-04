"""
Chart Generation Module
Creates visualization data for technical indicators, LSTM predictions, and sentiment
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Generate chart data for frontend visualization"""
    
    @staticmethod
    def generate_price_chart(df: pd.DataFrame, limit: int = 90) -> Dict:
        """Generate OHLC price chart data"""
        df_recent = df.tail(limit).copy()
        df_recent['date'] = pd.to_datetime(df_recent['date'])
        
        return {
            'dates': df_recent['date'].dt.strftime('%Y-%m-%d').tolist(),
            'open': df_recent['open'].tolist(),
            'high': df_recent['high'].tolist(),
            'low': df_recent['low'].tolist(),
            'close': df_recent['close'].tolist(),
            'volume': df_recent['volume'].tolist()
        }
    
    @staticmethod
    def generate_technical_indicators_chart(df: pd.DataFrame, indicators: Dict) -> Dict:
        """Generate technical indicators overlay chart"""
        df_recent = df.tail(90).copy()
        df_recent['date'] = pd.to_datetime(df_recent['date'])
        
        from analysis.technical_analysis import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer(df)
        
        # Calculate indicators for all historical data
        close = df['close']
        from ta.momentum import RSIIndicator
        from ta.trend import MACD, SMAIndicator, EMAIndicator
        from ta.volatility import BollingerBands
        
        rsi_indicator = RSIIndicator(close=close, window=14)
        macd_indicator = MACD(close=close)
        sma_20 = SMAIndicator(close=close, window=20)
        sma_50 = SMAIndicator(close=close, window=50)
        ema_20 = EMAIndicator(close=close, window=20)
        bb = BollingerBands(close=close)
        
        # Get last 90 days
        return {
            'dates': df_recent['date'].dt.strftime('%Y-%m-%d').tolist(),
            'price': df_recent['close'].tolist(),
            'rsi': rsi_indicator.rsi().tail(90).tolist(),
            'macd': macd_indicator.macd().tail(90).tolist(),
            'macd_signal': macd_indicator.macd_signal().tail(90).tolist(),
            'sma_20': sma_20.sma_indicator().tail(90).tolist(),
            'sma_50': sma_50.sma_indicator().tail(90).tolist(),
            'ema_20': ema_20.ema_indicator().tail(90).tolist(),
            'bb_upper': bb.bollinger_hband().tail(90).tolist(),
            'bb_middle': bb.bollinger_mavg().tail(90).tolist(),
            'bb_lower': bb.bollinger_lband().tail(90).tolist(),
            'volume': df_recent['volume'].tolist()
        }
    
    @staticmethod
    def generate_lstm_prediction_chart(historical_data: List[float], 
                                      predictions: List[float],
                                      dates: List[str],
                                      future_dates: List[str]) -> Dict:
        """Generate LSTM prediction vs actual chart"""
        
        # Take last 30 days of historical data for context
        historical_recent = historical_data[-30:] if len(historical_data) > 30 else historical_data
        dates_recent = dates[-30:] if len(dates) > 30 else dates
        
        return {
            'historical_dates': dates_recent,
            'historical_prices': historical_recent,
            'future_dates': future_dates,
            'predicted_prices': predictions
        }
    
    @staticmethod
    def generate_sentiment_gauge(sentiment_score: float) -> Dict:
        """Generate sentiment gauge data"""
        
        # Normalize sentiment score to 0-100 scale
        normalized = ((sentiment_score + 1) / 2) * 100
        
        if normalized >= 70:
            color = '#27ae60'
            label = 'Very Positive'
        elif normalized >= 55:
            color = '#2ecc71'
            label = 'Positive'
        elif normalized >= 45:
            color = '#f39c12'
            label = 'Neutral'
        elif normalized >= 30:
            color = '#e67e22'
            label = 'Negative'
        else:
            color = '#e74c3c'
            label = 'Very Negative'
        
        return {
            'score': normalized,
            'color': color,
            'label': label
        }
    
    @staticmethod
    def generate_signals_distribution(signals: Dict) -> Dict:
        """Generate signals distribution pie chart data"""
        
        buy = sum(1 for s in signals.values() if 'BUY' in str(s).upper())
        sell = sum(1 for s in signals.values() if 'SELL' in str(s).upper())
        hold = sum(1 for s in signals.values() if 'HOLD' in str(s).upper())
        
        return {
            'labels': ['Buy Signals', 'Sell Signals', 'Hold Signals'],
            'values': [buy, sell, hold],
            'colors': ['#27ae60', '#e74c3c', '#f39c12']
        }
