"""
Factory Pattern Implementation for Price Data Service
services/price_service/factory.py
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import os


class PriceDataSourceFactory:
    """
    Factory Pattern: Creates appropriate price data source based on configuration
    Implements Factory Method pattern for creating data sources
    """
    
    _sources = {}
    
    @classmethod
    def register_source(cls, source_type: str, source_class):
        """Register a new data source type"""
        cls._sources[source_type] = source_class
    
    @classmethod
    def create_source(cls, source_type: str, config: Dict[str, Any]):
        """Create a data source instance based on type and configuration"""
        if source_type not in cls._sources:
            raise ValueError(f"Unknown source type: {source_type}")
        
        source_class = cls._sources[source_type]
        return source_class(config)
    
    @classmethod
    def get_available_sources(cls) -> list:
        """Get list of available source types"""
        return list(cls._sources.keys())


class ConfigurationManager:
    """
    Singleton Pattern: Manages application configuration
    Ensures single point of configuration access
    """
    
    _instance = None
    _config = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigurationManager, cls).__new__(cls)
                    cls._instance._load_configuration()
        return cls._instance
    
    def _load_configuration(self):
        """Load configuration from environment variables and config files"""
        # Load from environment variables with error handling
        try:
            self._config = {
                'data_sources': os.getenv('DATA_SOURCES', 'file').split(','),
                'default_timeframe': os.getenv('DEFAULT_TIMEFRAME', '1h'),
                'max_data_points': self._safe_int_conversion(os.getenv('MAX_DATA_POINTS', '1000'), 'MAX_DATA_POINTS', 1000),
                'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
                'api_rate_limit': self._safe_int_conversion(os.getenv('API_RATE_LIMIT', '100'), 'API_RATE_LIMIT', 100),
            }
        except Exception as e:
            print(f"Error loading configuration from environment variables: {e}")
            # Fallback to default configuration
            self._config = {
                'data_sources': ['file'],
                'default_timeframe': '1h',
                'max_data_points': 1000,
                'cache_enabled': True,
                'api_rate_limit': 100,
            }
        
        # Load file paths from config file if exists
        config_file = os.getenv('CONFIG_FILE', 'config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file {config_file}: {e}")
    
    def _safe_int_conversion(self, value: str, env_var: str, default: int) -> int:
        """Safely convert environment variable to int"""
        try:
            return int(value)
        except (ValueError, TypeError):
            print(f"Invalid value for {env_var}: '{value}'. Using default: {default}")
            return default
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()


class CacheManager:
    """
    Singleton Pattern: Manages data caching across the service
    Provides efficient data caching with TTL support
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CacheManager, cls).__new__(cls)
                    cls._instance._cache = {}
                    cls._instance._ttl = {}
        return cls._instance
    
    def get(self, key: str):
        """Get cached value if not expired"""
        import time
        
        with self._lock:
            if key in self._cache:
                if key in self._ttl:
                    if time.time() < self._ttl[key]:
                        return self._cache[key]
                    else:
                        # Expired, remove from cache
                        del self._cache[key]
                        del self._ttl[key]
                else:
                    # No TTL set, apply default TTL of 30 minutes
                    self._ttl[key] = time.time() + 1800
                    return self._cache[key]
        return None
    
    def set(self, key: str, value, ttl_seconds: int = None):
        """Set value in cache with optional TTL"""
        import time
        
        with self._lock:
            self._cache[key] = value
            if ttl_seconds:
                self._ttl[key] = time.time() + ttl_seconds
            else:
                # Apply default TTL of 30 minutes if not specified
                self._ttl[key] = time.time() + 1800
        
        # Periodically cleanup expired entries
        if len(self._cache) % 50 == 0:  # Cleanup every 50 operations
            self.cleanup_expired()
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._ttl.clear()
    
    def remove(self, key: str):
        """Remove specific key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        import time
        
        with self._lock:
            current_time = time.time()
            expired_keys = [key for key, expiry_time in self._ttl.items() if current_time >= expiry_time]
            
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                del self._ttl[key]


class LoggerManager:
    """
    Singleton Pattern: Centralized logging management
    Provides consistent logging across the service
    """
    
    _instance = None
    _logger = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LoggerManager, cls).__new__(cls)
                    cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup logger configuration"""
        import logging
        import sys
        
        # Use default configuration first to avoid circular dependency
        log_level = 'INFO'
        log_file = 'price_service.log'
        
        # Try to get configuration from environment directly to avoid circular dependency
        log_level_env = os.getenv('LOG_LEVEL', 'INFO')
        log_file_env = os.getenv('LOG_FILE', 'price_service.log')
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level_env.upper() in valid_levels:
            log_level = log_level_env.upper()
        
        if log_file_env:
            log_file = log_file_env
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file)
            ]
        )
        
        self._logger = logging.getLogger('price_service')
    
    def get_logger(self):
        """Get logger instance"""
        return self._logger
    
    def log_request(self, endpoint: str, params: Dict[str, Any], response_time: float):
        """Log API request details"""
        self._logger.info(f"Request: {endpoint} | Params: {params} | Time: {response_time:.2f}s")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with context"""
        self._logger.error(f"Error in {context}: {str(error)}", exc_info=True)
