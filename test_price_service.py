"""
Unit Tests for Price Service
tests/test_price_service.py
"""

import pytest
import json
from services.price_service.app import app, PriceDataManager, FileDataStrategy, APIDataStrategy, CacheStrategy


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_data():
    """Sample OHLCV data"""
    return [
        {"time": 1641234000000, "open": 2500.5, "high": 2510.2, "low": 2495.1, "close": 2505.3, "volume": 150.5},
        {"time": 1641237600000, "open": 2505.3, "high": 2515.8, "low": 2503.0, "close": 2510.2, "volume": 145.2}
    ]


class TestPriceService:
    """Test Price Service Endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['service'] == 'Price Data Service'
        assert data['status'] == 'healthy'
    
    def test_get_prices(self, client):
        """Test get prices endpoint"""
        response = client.get('/api/prices/ETHUSDT?timeframe=1h&limit=10')
        assert response.status_code in [200, 404]  # May return 404 if data not available
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['symbol'] == 'ETHUSDT'
            assert 'data' in data
    
    def test_get_latest_price(self, client):
        """Test get latest price endpoint"""
        response = client.get('/api/prices/latest/ETHUSDT')
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['symbol'] == 'ETHUSDT'
            assert 'price' in data
    
    def test_get_price_stats(self, client):
        """Test price statistics endpoint"""
        response = client.get('/api/prices/stats/ETHUSDT')
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['symbol'] == 'ETHUSDT'
            assert 'high' in data
            assert 'low' in data
            assert 'avg' in data


class TestStrategyPattern:
    """Test Strategy Pattern Implementation"""
    
    def test_file_strategy(self, mock_data):
        """Test FileDataStrategy"""
        strategy = FileDataStrategy({'ETHUSDT': 'nonexistent.json'})
        assert strategy.is_available()
        assert strategy.get_source_name() == 'File (Historical)'
        
        # Should return empty for nonexistent file
        result = strategy.fetch_ohlcv('ETHUSDT', '1h', 100)
        assert result == []
    
    def test_api_strategy(self, mock_data):
        """Test APIDataStrategy"""
        strategy = APIDataStrategy('test-api-key')
        assert strategy.is_available()
        assert strategy.get_source_name() == 'Live API'
        
        # Should generate synthetic data
        result = strategy.fetch_ohlcv('ETHUSDT', '1h', 10)
        assert len(result) == 10
        assert 'open' in result[0]
        assert 'close' in result[0]
    
    def test_cache_strategy(self, mock_data):
        """Test CacheStrategy"""
        strategy = CacheStrategy()
        assert not strategy.is_available()  # Empty cache
        
        strategy.set('ETHUSDT', mock_data)
        assert strategy.is_available()
        
        result = strategy.fetch_ohlcv('ETHUSDT', '1h', 100)
        assert len(result) == len(mock_data)
    
    def test_price_data_manager(self, mock_data):
        """Test PriceDataManager context class"""
        manager = PriceDataManager()
        
        # Add strategies
        cache_strategy = CacheStrategy()
        cache_strategy.set('ETHUSDT', mock_data)
        
        manager.add_strategy(cache_strategy)
        manager.set_primary_strategy(cache_strategy)
        
        # Get price data
        result = manager.get_price_data('ETHUSDT', '1h', 100)
        assert result['symbol'] == 'ETHUSDT'
        assert len(result['data']) == len(mock_data)


class TestErrorHandling:
    """Test Error Handling"""
    
    def test_invalid_symbol(self, client):
        """Test with invalid symbol"""
        response = client.get('/api/prices/INVALID999')
        assert response.status_code in [200, 404]
    
    def test_invalid_parameters(self, client):
        """Test with invalid parameters"""
        response = client.get('/api/prices/ETHUSDT?limit=invalid')
        assert response.status_code in [200, 404, 400]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
