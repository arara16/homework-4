"""
Unit Tests for Technical Analysis Service
tests/test_ta_service.py
"""

import pytest
import json
import numpy as np
from services.ta_service.app import app, TACalculator, RSIStrategy, MACDStrategy, BollingerBandsStrategy, MovingAverageStrategy


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_prices():
    """Generate sample price data"""
    np.random.seed(42)
    base_price = 2500
    prices = []
    for i in range(100):
        prices.append(base_price + np.random.normal(0, 50))
    return prices


class TestTechnicalAnalysisService:
    """Test TA Service Endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['service'] == 'Technical Analysis Service'
        assert data['status'] == 'healthy'


class TestIndicatorStrategies:
    """Test Individual Indicator Strategies"""
    
    def test_rsi_strategy(self, sample_prices):
        """Test RSI calculation"""
        strategy = RSIStrategy()
        result = strategy.calculate(sample_prices)
        
        assert result['indicator'] == 'RSI'
        assert 'value' in result
        assert 'overbought' in result
        assert 'oversold' in result
        assert result['value'] >= 0 and result['value'] <= 100
    
    def test_macd_strategy(self, sample_prices):
        """Test MACD calculation"""
        strategy = MACDStrategy()
        result = strategy.calculate(sample_prices)
        
        assert result['indicator'] == 'MACD'
        assert 'macd_line' in result
        assert 'signal_line' in result
        assert 'histogram' in result
        assert 'bullish' in result
    
    def test_bollinger_bands_strategy(self, sample_prices):
        """Test Bollinger Bands calculation"""
        strategy = BollingerBandsStrategy()
        result = strategy.calculate(sample_prices)
        
        assert result['indicator'] == 'Bollinger Bands'
        assert 'upper_band' in result
        assert 'middle_band' in result
        assert 'lower_band' in result
        assert 'position' in result
        assert result['upper_band'] > result['middle_band'] > result['lower_band']
    
    def test_moving_average_strategy(self, sample_prices):
        """Test Moving Average calculation"""
        strategy = MovingAverageStrategy()
        result = strategy.calculate(sample_prices)
        
        assert result['indicator'] == 'Moving Averages'
        assert 'sma_short' in result
        assert 'sma_long' in result
        assert 'trend' in result
        assert result['trend'] in ['bullish', 'bearish']


class TestTACalculator:
    """Test TA Calculator Context Class"""
    
    def test_calculate_all_indicators(self, sample_prices):
        """Test calculating all indicators"""
        calculator = TACalculator()
        result = calculator.calculate_all(sample_prices)
        
        assert 'rsi' in result
        assert 'macd' in result
        assert 'bb' in result
        assert 'ma' in result
        assert 'timestamp' in result
    
    def test_calculate_single_indicator(self, sample_prices):
        """Test calculating single indicator"""
        calculator = TACalculator()
        
        result_rsi = calculator.calculate('rsi', sample_prices)
        assert result_rsi['indicator'] == 'RSI'
        
        result_macd = calculator.calculate('macd', sample_prices)
        assert result_macd['indicator'] == 'MACD'
    
    def test_calculate_invalid_indicator(self, sample_prices):
        """Test with invalid indicator"""
        calculator = TACalculator()
        result = calculator.calculate('invalid', sample_prices)
        
        assert 'error' in result


class TestSignalGeneration:
    """Test Trading Signal Generation"""
    
    def test_signal_generation(self, sample_prices):
        """Test automated signal generation"""
        calculator = TACalculator()
        
        # Get all indicators
        result = calculator.calculate_all(sample_prices)
        
        # Should have valid indicators
        assert result['rsi']['indicator'] == 'RSI'
        assert result['macd']['indicator'] == 'MACD'
        assert result['bb']['indicator'] == 'Bollinger Bands'
        assert result['ma']['indicator'] == 'Moving Averages'


class TestEdgeCases:
    """Test Edge Cases and Error Handling"""
    
    def test_insufficient_data(self):
        """Test with insufficient data"""
        strategy = RSIStrategy()
        short_prices = [100, 101, 102]  # Too short
        result = strategy.calculate(short_prices)
        
        assert 'error' in result or result['value'] is not None
    
    def test_empty_prices(self):
        """Test with empty prices"""
        strategy = RSIStrategy()
        result = strategy.calculate([])
        assert 'error' in result
    
    def test_constant_prices(self):
        """Test with constant prices"""
        strategy = RSIStrategy()
        constant_prices = [100] * 50
        result = strategy.calculate(constant_prices)
        
        # Should not crash, RSI should be around 50 (neutral)
        assert result['indicator'] == 'RSI'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
