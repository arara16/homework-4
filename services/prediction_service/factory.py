"""
Factory Pattern Implementation for Prediction Service
services/prediction_service/factory.py
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os
import threading


class PredictionModelFactory:
    """
    Factory Pattern: Creates appropriate prediction models based on configuration
    Implements Factory Method pattern for creating prediction strategies
    """
    
    _models = {}
    
    @classmethod
    def register_model(cls, model_type: str, model_class):
        """Register a new prediction model type"""
        cls._models[model_type] = model_class
    
    @classmethod
    def create_model(cls, model_type: str, config: Dict[str, Any]):
        """Create a prediction model instance based on type and configuration"""
        if model_type not in cls._models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_class = cls._models[model_type]
        return model_class(config)
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available model types"""
        return list(cls._models.keys())


class ModelTrainerFactory:
    """
    Factory Pattern: Creates appropriate model trainers
    Handles different training strategies for various model types
    """
    
    _trainers = {}
    
    @classmethod
    def register_trainer(cls, trainer_type: str, trainer_class):
        """Register a new trainer type"""
        cls._trainers[trainer_type] = trainer_class
    
    @classmethod
    def create_trainer(cls, trainer_type: str, config: Dict[str, Any]):
        """Create a trainer instance based on type and configuration"""
        if trainer_type not in cls._trainers:
            raise ValueError(f"Unknown trainer type: {trainer_type}")
        
        trainer_class = cls._trainers[trainer_type]
        return trainer_class(config)


class ConfigurationManager:
    """
    Singleton Pattern: Manages prediction service configuration
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
        # Load from environment variables
        self._config = {
            'default_model': os.getenv('DEFAULT_MODEL', 'lstm'),
            'lookback_period': int(os.getenv('LOOKBACK_PERIOD', '30')),
            'forecast_days': int(os.getenv('FORECAST_DAYS', '7')),
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.7')),
            'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'cache_ttl': int(os.getenv('CACHE_TTL', '3600')),  # 1 hour
            'batch_size': int(os.getenv('BATCH_SIZE', '32')),
            'epochs': int(os.getenv('EPOCHS', '100')),
            'validation_split': float(os.getenv('VALIDATION_SPLIT', '0.2')),
        }
        
        # Load model configurations
        model_configs = os.getenv('MODEL_CONFIGS', '{}')
        try:
            self._config['model_configs'] = json.loads(model_configs)
        except json.JSONDecodeError:
            self._config['model_configs'] = {}
        
        # Load from config file if exists
        config_file = os.getenv('CONFIG_FILE', 'prediction_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self._config[key] = value
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get configuration for a specific model type"""
        return self._config.get('model_configs', {}).get(model_type, {})
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()


class CacheManager:
    """
    Singleton Pattern: Manages prediction caching across the service
    Provides efficient caching with TTL support for predictions
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
                    cls._instance._access_times = {}
        return cls._instance
    
    def get(self, key: str):
        """Get cached prediction if not expired"""
        import time
        
        with self._lock:
            if key in self._cache:
                if key in self._ttl:
                    if time.time() < self._ttl[key]:
                        self._access_times[key] = time.time()
                        return self._cache[key]
                    else:
                        # Expired, remove from cache
                        del self._cache[key]
                        del self._ttl[key]
                        if key in self._access_times:
                            del self._access_times[key]
                else:
                    self._access_times[key] = time.time()
                    return self._cache[key]
        return None
    
    def set(self, key: str, value, ttl_seconds: int = None):
        """Set prediction in cache with optional TTL"""
        import time
        
        with self._lock:
            self._cache[key] = value
            self._access_times[key] = time.time()
            if ttl_seconds:
                self._ttl[key] = time.time() + ttl_seconds
    
    def clear(self):
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            self._ttl.clear()
            self._access_times.clear()
    
    def remove(self, key: str):
        """Remove specific key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
            if key in self._access_times:
                del self._access_times[key]
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        import time
        
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, expiry_time in self._ttl.items():
                if current_time >= expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                del self._ttl[key]
                if key in self._access_times:
                    del self._access_times[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        import time
        
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for expiry in self._ttl.values() if time.time() >= expiry)
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'valid_entries': total_entries - expired_entries,
                'cache_keys': list(self._cache.keys())
            }


class LoggerManager:
    """
    Singleton Pattern: Centralized logging management for prediction service
    Provides consistent logging with structured format
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
        
        config_manager = ConfigurationManager()
        log_level = config_manager.get('log_level', 'INFO')
        log_file = config_manager.get('log_file', 'prediction_service.log')
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Setup handlers
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
        
        # Configure formatter for each handler
        for handler in handlers:
            handler.setFormatter(formatter)
        
        # Configure logger
        logging.basicConfig(
            level=getattr(logging, log_level),
            handlers=handlers,
            force=True
        )
        
        self._logger = logging.getLogger('prediction_service')
    
    def get_logger(self):
        """Get logger instance"""
        return self._logger
    
    def log_prediction_request(self, symbol: str, model: str, params: Dict[str, Any], response_time: float):
        """Log prediction request details"""
        self._logger.info(f"PREDICTION_REQUEST - Symbol: {symbol}, Model: {model}, "
                         f"Params: {params}, ResponseTime: {response_time:.2f}s")
    
    def log_model_training(self, model: str, symbol: str, epochs: int, loss: float, accuracy: float):
        """Log model training details"""
        self._logger.info(f"MODEL_TRAINING - Model: {model}, Symbol: {symbol}, "
                         f"Epochs: {epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
    
    def log_error(self, error: Exception, context: str = "", extra_data: Dict[str, Any] = None):
        """Log error with context and extra data"""
        error_msg = f"Error in {context}: {str(error)}"
        if extra_data:
            error_msg += f" | Extra: {extra_data}"
        self._logger.error(error_msg, exc_info=True)
    
    def log_cache_operation(self, operation: str, key: str, hit: bool = None):
        """Log cache operations"""
        if hit is not None:
            status = "HIT" if hit else "MISS"
            self._logger.debug(f"CACHE_{operation.upper()} - Key: {key}, Status: {status}")
        else:
            self._logger.debug(f"CACHE_{operation.upper()} - Key: {key}")
