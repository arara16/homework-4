"""
Observer Pattern Implementation for Prediction Service
services/prediction_service/observer.py
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import threading


class Observer(ABC):
    """
    Abstract Observer interface
    Defines the contract for observers that react to prediction events
    """
    
    @abstractmethod
    def update(self, subject, event_type: str, data: Dict[str, Any]):
        """Called when the observed subject changes state"""
        pass


class Subject(ABC):
    """
    Abstract Subject interface
    Defines the contract for subjects that can be observed
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._lock = threading.Lock()
    
    def attach(self, observer: Observer):
        """Attach an observer to this subject"""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Detach an observer from this subject"""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]):
        """Notify all observers of an event"""
        with self._lock:
            observers_copy = self._observers.copy()
        
        for observer in observers_copy:
            try:
                observer.update(self, event_type, data)
            except Exception as e:
                # Use proper logging instead of print
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error notifying observer {observer.__class__.__name__}: {e}", exc_info=True)


class PredictionSubject(Subject):
    """
    Concrete Subject for prediction events
    Manages prediction state and notifies observers of changes
    """
    
    def __init__(self):
        super().__init__()
        self._predictions = {}
        self._models = {}
        self._last_update = {}
    
    def add_prediction(self, symbol: str, prediction: Dict[str, Any]):
        """Add a new prediction and notify observers"""
        self._predictions[symbol] = prediction
        self._last_update[symbol] = datetime.now()
        
        self.notify('prediction_added', {
            'symbol': symbol,
            'prediction': prediction,
            'timestamp': self._last_update[symbol].isoformat()
        })
    
    def update_prediction(self, symbol: str, prediction: Dict[str, Any]):
        """Update an existing prediction and notify observers"""
        if symbol in self._predictions:
            self._predictions[symbol] = prediction
            self._last_update[symbol] = datetime.now()
            
            self.notify('prediction_updated', {
                'symbol': symbol,
                'prediction': prediction,
                'timestamp': self._last_update[symbol].isoformat()
            })
    
    def get_prediction(self, symbol: str) -> Dict[str, Any]:
        """Get prediction for a symbol"""
        return self._predictions.get(symbol, {})
    
    def get_all_predictions(self) -> Dict[str, Dict[str, Any]]:
        """Get all predictions"""
        return self._predictions.copy()


class DataUpdateSubject(Subject):
    """
    Concrete Subject for data update events
    Notifies observers when new market data is available
    """
    
    def __init__(self):
        super().__init__()
        self._data_sources = {}
        self._last_data_update = {}
    
    def notify_data_update(self, source: str, symbol: str, data: List[Dict[str, Any]]):
        """Notify observers of new data"""
        self._last_data_update[f"{source}_{symbol}"] = datetime.now()
        
        self.notify('data_updated', {
            'source': source,
            'symbol': symbol,
            'data_count': len(data),
            'timestamp': datetime.now().isoformat()
        })
    
    def get_last_update(self, source: str, symbol: str) -> datetime:
        """Get last update time for a data source"""
        key = f"{source}_{symbol}"
        return self._last_data_update.get(key)


class PredictionLoggerObserver(Observer):
    """
    Concrete Observer: Logs prediction events
    Provides detailed logging of prediction activities
    """
    
    def __init__(self, log_file: str = 'prediction_events.log'):
        self.log_file = log_file
    
    def update(self, subject, event_type: str, data: Dict[str, Any]):
        """Log prediction events to file"""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {event_type}: {data}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            # Use proper logging instead of print
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error writing to log file {self.log_file}: {e}", exc_info=True)


class CacheInvalidationObserver(Observer):
    """
    Concrete Observer: Invalidates cache when predictions are updated
    Ensures cache consistency when predictions change
    """
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def update(self, subject, event_type: str, data: Dict[str, Any]):
        """Invalidate cache entries for updated predictions"""
        if event_type in ['prediction_added', 'prediction_updated']:
            symbol = data.get('symbol')
            if symbol:
                # Remove cached predictions for this symbol
                cache_keys = [
                    f"prediction_{symbol}",
                    f"analysis_{symbol}",
                    f"forecast_{symbol}"
                ]
                
                for key in cache_keys:
                    self.cache_manager.remove(key)
                
                # Use proper logging instead of print
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Invalidated cache for symbol: {symbol}")


class NotificationObserver(Observer):
    """
    Concrete Observer: Sends notifications for important prediction events
    Can be extended to send emails, webhooks, etc.
    """
    
    def __init__(self):
        self.notification_threshold = 0.8  # Confidence threshold for notifications
    
    def update(self, subject, event_type: str, data: Dict[str, Any]):
        """Send notifications for high-confidence predictions"""
        if event_type == 'prediction_added':
            prediction = data.get('prediction', {})
            confidence = prediction.get('confidence', 0)
            symbol = data.get('symbol')
            
            if confidence >= self.notification_threshold:
                self._send_notification(symbol, prediction)
    
    def _send_notification(self, symbol: str, prediction: Dict[str, Any]):
        """Send notification (placeholder implementation)"""
        message = f"High confidence prediction for {symbol}: {prediction.get('forecast', 'N/A')}"
        
        # Use proper logging instead of print
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"NOTIFICATION: {message}")
        
        # In a real implementation, this could send:
        # - Email notifications
        # - Slack messages
        # - Webhook calls
        # - SMS alerts


class PredictionEventManager:
    """
    Manager class for observer pattern implementation
    Provides easy access to subjects and observers
    """
    
    def __init__(self):
        self.prediction_subject = PredictionSubject()
        self.data_update_subject = DataUpdateSubject()
        
        # Register default observers
        self._setup_default_observers()
    
    def _setup_default_observers(self):
        """Setup default observers for the prediction service"""
        # Add logging observer
        logger_observer = PredictionLoggerObserver()
        self.prediction_subject.attach(logger_observer)
        
        # Add cache invalidation observer (if cache manager available)
        try:
            from .factory import CacheManager
            cache_manager = CacheManager()
            cache_observer = CacheInvalidationObserver(cache_manager)
            self.prediction_subject.attach(cache_observer)
        except ImportError:
            pass
        
        # Add notification observer
        notification_observer = NotificationObserver()
        self.prediction_subject.attach(notification_observer)
    
    def get_prediction_subject(self) -> PredictionSubject:
        """Get the prediction subject"""
        return self.prediction_subject
    
    def get_data_update_subject(self) -> DataUpdateSubject:
        """Get the data update subject"""
        return self.data_update_subject
    
    def add_custom_observer(self, observer: Observer, subject_type: str = 'prediction'):
        """Add a custom observer to a specific subject"""
        if subject_type == 'prediction':
            self.prediction_subject.attach(observer)
        elif subject_type == 'data':
            self.data_update_subject.attach(observer)
        else:
            raise ValueError(f"Unknown subject type: {subject_type}")
