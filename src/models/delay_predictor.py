"""
Delay Predictor Model
Simple ML model to predict public transport delays based on weather
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DelayPredictor:
    """Predicts public transport delays based on weather conditions"""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
    def create_training_data(self, weather_data: pd.DataFrame, 
                           delay_data: pd.DataFrame) -> pd.DataFrame:
        """
        Create training dataset by combining weather and delay data
        
        Args:
            weather_data: Processed weather features
            delay_data: Historical delay data
        """
        # For PoC, we'll create synthetic training data
        # In real implementation, this would merge actual historical data
        
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic training data
        training_data = []
        
        for i in range(n_samples):
            # Random weather conditions
            temp = np.random.normal(5, 15)  # Temperature around 5°C ± 15
            precip = np.random.exponential(2)  # Precipitation (exponential distribution)
            wind = np.random.exponential(5)  # Wind speed
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            is_weekend = 1 if day_of_week in [5, 6] else 0
            
            # Calculate weather severity
            weather_score = 0
            if precip > 5:
                weather_score += 3
            elif precip > 1:
                weather_score += 1
            if temp < -5:
                weather_score += 2
            elif temp < 0:
                weather_score += 1
            if wind > 10:
                weather_score += 1
            
            # Rush hour factor
            rush_hour = 1 if (hour >= 7 and hour <= 9) or (hour >= 16 and hour <= 18) else 0
            
            # Predict delay based on conditions (synthetic relationship)
            base_delay = 2  # Base delay in minutes
            weather_delay = weather_score * 1.5  # Weather impact
            rush_delay = rush_hour * 2  # Rush hour impact
            weekend_factor = 0.5 if is_weekend else 1.0  # Less traffic on weekends
            
            # Add some randomness
            noise = np.random.normal(0, 1)
            
            predicted_delay = max(0, (base_delay + weather_delay + rush_delay) * weekend_factor + noise)
            
            training_data.append({
                'temperature_c': temp,
                'precipitation_mm': precip,
                'wind_speed_ms': wind,
                'weather_severity_score': weather_score,
                'hour': hour,
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'rush_hour': rush_hour,
                'delay_minutes': predicted_delay
            })
        
        return pd.DataFrame(training_data)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and target for training
        
        Args:
            df: Training DataFrame
        """
        # Define feature columns
        feature_cols = [
            'temperature_c', 'precipitation_mm', 'wind_speed_ms',
            'weather_severity_score', 'hour', 'day_of_week',
            'is_weekend', 'rush_hour'
        ]
        
        self.feature_names = feature_cols
        
        X = df[feature_cols].values
        y = df['delay_minutes'].values
        
        return X, y
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train the delay prediction model
        
        Args:
            training_data: DataFrame with features and target
        """
        try:
            # Prepare features and target
            X, y = self.prepare_features(training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Initialize model
            if self.model_type == "random_forest":
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            elif self.model_type == "linear":
                self.model = LinearRegression()
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred_train = self.model.predict(X_train_scaled)
            y_pred_test = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            metrics = {
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test)
            }
            
            self.is_trained = True
            
            logger.info(f"Model trained successfully. Test R²: {metrics['test_r2']:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {}
    
    def predict_delay(self, weather_features: Dict) -> Dict:
        """
        Predict delay based on weather features
        
        Args:
            weather_features: Dictionary with weather features
        """
        if not self.is_trained:
            logger.error("Model not trained yet")
            return {'predicted_delay': 0, 'confidence': 0}
        
        try:
            # Prepare feature vector
            features = []
            for col in self.feature_names:
                features.append(weather_features.get(col, 0))
            
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            predicted_delay = self.model.predict(X_scaled)[0]
            
            # Calculate confidence (for Random Forest)
            if hasattr(self.model, 'estimators_'):
                predictions = []
                for estimator in self.model.estimators_:
                    pred = estimator.predict(X_scaled)[0]
                    predictions.append(pred)
                confidence = 1 - np.std(predictions) / (np.mean(predictions) + 1e-8)
            else:
                confidence = 0.8  # Default confidence for linear models
            
            return {
                'predicted_delay_minutes': max(0, predicted_delay),
                'confidence': min(1.0, max(0.0, confidence)),
                'weather_severity': weather_features.get('weather_severity_score', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {'predicted_delay_minutes': 0, 'confidence': 0}
    
    def save_model(self, filepath: str) -> bool:
        """Save trained model"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'model_type': self.model_type,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_type = model_data['model_type']
            self.is_trained = model_data['is_trained']
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

if __name__ == "__main__":
    # Test the delay predictor
    predictor = DelayPredictor(model_type="random_forest")
    
    # Create synthetic training data
    training_data = predictor.create_training_data(None, None)
    
    # Train model
    metrics = predictor.train(training_data)
    print("Training metrics:", metrics)
    
    # Test prediction
    test_features = {
        'temperature_c': -2,
        'precipitation_mm': 8,
        'wind_speed_ms': 12,
        'weather_severity_score': 6,
        'hour': 8,
        'day_of_week': 1,
        'is_weekend': 0,
        'rush_hour': 1
    }
    
    prediction = predictor.predict_delay(test_features)
    print("Prediction:", prediction)
    
    # Save model
    predictor.save_model("data/models/delay_predictor.pkl")
