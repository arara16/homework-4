import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, ADXIndicator, CCIIndicator, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date')
        
    def calculate_oscillators(self) -> Dict[str, float]:
        close = self.df['close']
        high = self.df['high']
        low = self.df['low']
        oscillators = {}
        
        try:
            rsi = RSIIndicator(close=close, window=14)
            oscillators['RSI'] = float(rsi.rsi().iloc[-1])
            
            macd = MACD(close=close)
            oscillators['MACD'] = float(macd.macd().iloc[-1])
            oscillators['MACD_Signal'] = float(macd.macd_signal().iloc[-1])
            oscillators['MACD_Diff'] = float(macd.macd_diff().iloc[-1])
            
            stoch = StochasticOscillator(high=high, low=low, close=close)
            oscillators['Stochastic_K'] = float(stoch.stoch().iloc[-1])
            oscillators['Stochastic_D'] = float(stoch.stoch_signal().iloc[-1])
            
            adx = ADXIndicator(high=high, low=low, close=close)
            oscillators['ADX'] = float(adx.adx().iloc[-1])
            
            cci = CCIIndicator(high=high, low=low, close=close)
            oscillators['CCI'] = float(cci.cci().iloc[-1])
        except Exception as e:
            logger.error(f"Error calculating oscillators: {e}")
            
        return oscillators
    
    def calculate_moving_averages(self) -> Dict[str, float]:
        close = self.df['close']
        volume = self.df['volume']
        mas = {}
        
        try:
            sma_20 = SMAIndicator(close=close, window=20)
            sma_50 = SMAIndicator(close=close, window=50)
            mas['SMA_20'] = float(sma_20.sma_indicator().iloc[-1])
            mas['SMA_50'] = float(sma_50.sma_indicator().iloc[-1])
            
            ema_20 = EMAIndicator(close=close, window=20)
            ema_50 = EMAIndicator(close=close, window=50)
            mas['EMA_20'] = float(ema_20.ema_indicator().iloc[-1])
            mas['EMA_50'] = float(ema_50.ema_indicator().iloc[-1])
            
            if len(close) >= 20:
                weights = np.arange(1, 21)
                mas['WMA_20'] = float(close.iloc[-20:].dot(weights) / weights.sum())
            
            bollinger = BollingerBands(close=close)
            mas['BB_Upper'] = float(bollinger.bollinger_hband().iloc[-1])
            mas['BB_Middle'] = float(bollinger.bollinger_mavg().iloc[-1])
            mas['BB_Lower'] = float(bollinger.bollinger_lband().iloc[-1])
            
            volume_sma = SMAIndicator(close=volume, window=20)
            mas['Volume_MA_20'] = float(volume_sma.sma_indicator().iloc[-1])
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            
        return mas
    
    def generate_signals(self) -> Dict[str, str]:
        oscillators = self.calculate_oscillators()
        mas = self.calculate_moving_averages()
        signals = {}
        current_price = self.df['close'].iloc[-1]
        
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
        
        return signals
    
    def get_comprehensive_analysis(self) -> Dict:
        """Analyze using last 1 day, 7 days (1 week), and 30 days (1 month) of data"""
        analysis = {}
        
        # Analyze using different lookback periods on daily data
        timeframes = {
            '1d': 1,      # Last 1 day
            '1w': 7,      # Last 7 days (1 week)
            '1m': 30      # Last 30 days (1 month)
        }
        
        for tf_name, lookback_days in timeframes.items():
            # Get the last N days of data
            df_period = self.df.tail(max(lookback_days, 60)).copy()  # Need at least 60 for indicators
            
            analyzer = TechnicalAnalyzer(df_period)
            
            analysis[tf_name] = {
                'oscillators': analyzer.calculate_oscillators(),
                'moving_averages': analyzer.calculate_moving_averages(),
                'signals': analyzer.generate_signals(),
                'period_info': f'Analysis based on last {lookback_days} day(s) of data'
            }
        
        # Overall recommendation based on all signals
        all_signals = []
        for tf in ['1d', '1w', '1m']:
            signals = analysis[tf]['signals']
            all_signals.extend([s for s in signals.values() if s in ['BUY', 'SELL', 'HOLD']])
        
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
        
        return analysis
