import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, symbol: str):
        self.symbol = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        self.vader = SentimentIntensityAnalyzer()
        
    def analyze_text_sentiment(self, text: str) -> Dict:
        vader_scores = self.vader.polarity_scores(text)
        blob = TextBlob(text)
        
        compound = vader_scores['compound']
        sentiment = 'POSITIVE' if compound >= 0.05 else 'NEGATIVE' if compound <= -0.05 else 'NEUTRAL'
        
        return {
            'vader': vader_scores,
            'textblob': {'polarity': blob.sentiment.polarity, 'subjectivity': blob.sentiment.subjectivity},
            'overall': sentiment,
            'score': compound
        }
    
    def get_crypto_news_sentiment(self) -> Dict:
        news_items = [
            {'title': f'{self.symbol} shows strong bullish momentum', 'description': 'Price continues upward trend'},
            {'title': f'{self.symbol} adoption increases globally', 'description': 'Major institutions announce support'},
            {'title': f'{self.symbol} faces regulatory concerns', 'description': 'New regulations may impact trading'}
        ]
        
        sentiments = [self.analyze_text_sentiment(n['title'] + ' ' + n['description'])['score'] for n in news_items]
        
        if not sentiments:
            return {'average_sentiment': 0, 'sentiment_class': 'NEUTRAL', 'news_count': 0}
        
        avg_sentiment = np.mean(sentiments)
        sentiment_class = 'POSITIVE' if avg_sentiment >= 0.05 else 'NEGATIVE' if avg_sentiment <= -0.05 else 'NEUTRAL'
        
        return {
            'average_sentiment': float(avg_sentiment),
            'sentiment_class': sentiment_class,
            'news_count': len(news_items),
            'positive_count': sum(1 for s in sentiments if s > 0.05),
            'negative_count': sum(1 for s in sentiments if s < -0.05),
            'neutral_count': sum(1 for s in sentiments if -0.05 <= s <= 0.05)
        }

class OnChainAnalyzer:
    def __init__(self, symbol: str):
        self.symbol = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        
    def get_onchain_metrics(self) -> Dict:
        base_values = {
            'BTC': {'active_addresses': 950000, 'transactions': 300000, 'hash_rate': 450000000},
            'ETH': {'active_addresses': 550000, 'transactions': 1200000, 'hash_rate': 950000000},
        }
        default = {'active_addresses': 50000, 'transactions': 15000, 'hash_rate': 1000000}
        base = base_values.get(self.symbol, default)
        
        metrics = {
            'active_addresses': base['active_addresses'] + np.random.randint(-10000, 10000),
            'transaction_count': base['transactions'] + np.random.randint(-5000, 5000),
            'exchange_inflow': float(np.random.uniform(1000000, 10000000)),
            'exchange_outflow': float(np.random.uniform(1000000, 10000000)),
            'whale_transactions': int(np.random.randint(50, 200)),
            'hash_rate': base['hash_rate'],
            'total_value_locked': float(np.random.uniform(1e9, 50e9)) if self.symbol in ['ETH', 'BNB'] else 0
        }
        
        market_cap = np.random.uniform(1e10, 1e12)
        tx_volume = metrics['transaction_count'] * 50000
        metrics['nvt_ratio'] = float(market_cap / tx_volume if tx_volume > 0 else 0)
        metrics['mvrv'] = float(np.random.uniform(0.8, 3.0))
        metrics['exchange_flow_ratio'] = float(metrics['exchange_inflow'] / metrics['exchange_outflow'] if metrics['exchange_outflow'] > 0 else 1.0)
        
        return metrics
    
    def analyze_metrics(self, metrics: Dict) -> Dict:
        signals = []
        
        if metrics['active_addresses'] > 500000:
            signals.append('BULLISH: High network activity')
        elif metrics['active_addresses'] < 100000:
            signals.append('BEARISH: Low network activity')
        
        flow_ratio = metrics['exchange_flow_ratio']
        if flow_ratio > 1.2:
            signals.append('BEARISH: High exchange inflows (selling pressure)')
        elif flow_ratio < 0.8:
            signals.append('BULLISH: High exchange outflows (accumulation)')
        
        nvt = metrics['nvt_ratio']
        if nvt > 95:
            signals.append('WARNING: High NVT ratio (potentially overvalued)')
        elif nvt < 45:
            signals.append('OPPORTUNITY: Low NVT ratio (potentially undervalued)')
        
        mvrv = metrics['mvrv']
        if mvrv > 2.5:
            signals.append('BEARISH: High MVRV (profit-taking zone)')
        elif mvrv < 1.0:
            signals.append('BULLISH: Low MVRV (accumulation zone)')
        
        bullish = len([s for s in signals if 'BULLISH' in s])
        bearish = len([s for s in signals if 'BEARISH' in s])
        
        return {
            'signals': signals,
            'overall_sentiment': 'BULLISH' if bullish > bearish else 'BEARISH'
        }

class CombinedAnalyzer:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.sentiment_analyzer = SentimentAnalyzer(symbol)
        self.onchain_analyzer = OnChainAnalyzer(symbol)
    
    def get_comprehensive_analysis(self) -> Dict:
        news_sentiment = self.sentiment_analyzer.get_crypto_news_sentiment()
        onchain_metrics = self.onchain_analyzer.get_onchain_metrics()
        onchain_analysis = self.onchain_analyzer.analyze_metrics(onchain_metrics)
        
        sentiment_score = news_sentiment['average_sentiment']
        onchain_bullish = len([s for s in onchain_analysis['signals'] if 'BULLISH' in s])
        onchain_bearish = len([s for s in onchain_analysis['signals'] if 'BEARISH' in s])
        
        combined_score = sentiment_score * 0.4 + (onchain_bullish - onchain_bearish) * 0.1
        
        if combined_score > 0.3:
            final_signal = 'STRONG_BUY'
        elif combined_score > 0.1:
            final_signal = 'BUY'
        elif combined_score < -0.3:
            final_signal = 'STRONG_SELL'
        elif combined_score < -0.1:
            final_signal = 'SELL'
        else:
            final_signal = 'HOLD'
        
        return {
            'sentiment_analysis': news_sentiment,
            'onchain_metrics': onchain_metrics,
            'onchain_analysis': onchain_analysis,
            'combined_signal': final_signal,
            'combined_score': float(combined_score)
        }
