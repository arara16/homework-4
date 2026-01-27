import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from typing import Dict, Tuple
import logging
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class LSTMPredictor:
    def __init__(self, df: pd.DataFrame, lookback_period: int = 30):
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date')
        self.lookback_period = lookback_period
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
    def prepare_data(self, train_split: float = 0.7) -> Tuple:
        features = ['open', 'high', 'low', 'close', 'volume']
        data = self.df[features].values
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(self.lookback_period, len(scaled_data)):
            X.append(scaled_data[i-self.lookback_period:i])
            y.append(scaled_data[i, 3])
        
        X, y = np.array(X), np.array(y)
        split_idx = int(len(X) * train_split)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, y_train, X_test, y_test
    
    def build_model(self, input_shape: Tuple) -> Sequential:
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train(self, epochs: int = 50, batch_size: int = 32) -> Dict:
        X_train, y_train, X_test, y_test = self.prepare_data()
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
        
        early_stop = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        history = self.model.fit(
            X_train, y_train, epochs=epochs, batch_size=batch_size,
            validation_split=0.1, callbacks=[early_stop], verbose=0
        )
        
        predictions = self.model.predict(X_test, verbose=0)
        
        dummy = np.zeros((len(predictions), 5))
        dummy[:, 3] = predictions.flatten()
        predictions_actual = self.scaler.inverse_transform(dummy)[:, 3]
        
        dummy_test = np.zeros((len(y_test), 5))
        dummy_test[:, 3] = y_test
        y_test_actual = self.scaler.inverse_transform(dummy_test)[:, 3]
        
        rmse = np.sqrt(mean_squared_error(y_test_actual, predictions_actual))
        mape = mean_absolute_percentage_error(y_test_actual, predictions_actual) * 100
        r2 = r2_score(y_test_actual, predictions_actual)
        
        return {
            'history': {k: [float(v) for v in vals] for k, vals in history.history.items()},
            'metrics': {'RMSE': float(rmse), 'MAPE': float(mape), 'R2': float(r2)},
            'predictions': predictions_actual.tolist(),
            'actual': y_test_actual.tolist()
        }
    
    def predict_future(self, days: int = 7) -> Dict:
        if self.model is None:
            return {}
        
        features = ['open', 'high', 'low', 'close', 'volume']
        last_data = self.df[features].iloc[-self.lookback_period:].values
        scaled_last = self.scaler.transform(last_data)
        
        predictions = []
        current_input = scaled_last.copy()
        
        for _ in range(days):
            X_pred = current_input.reshape(1, self.lookback_period, 5)
            next_pred = self.model.predict(X_pred, verbose=0)[0, 0]
            
            dummy = np.zeros((1, 5))
            dummy[0, 3] = next_pred
            next_price = self.scaler.inverse_transform(dummy)[0, 3]
            predictions.append(float(next_price))
            
            next_row = np.array([[next_pred] * 5])
            current_input = np.vstack([current_input[1:], next_row])
        
        last_date = self.df['date'].iloc[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days, freq='D')
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'predictions': predictions,
            'current_price': float(self.df['close'].iloc[-1])
        }
    
    def get_comprehensive_prediction(self) -> Dict:
        training_results = self.train(epochs=50, batch_size=32)
        future_predictions = self.predict_future(days=7)
        
        return {
            'model_performance': training_results['metrics'],
            'future_predictions': future_predictions,
            'model_trained': True
        }
