"""
Weather Data Processor
Processes raw weather data into features for delay prediction
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherProcessor:
    """Processes weather data for delay prediction"""
    
    def __init__(self):
        self.weather_features = []
    
    def parse_smhi_data(self, weather_data: Dict) -> pd.DataFrame:
        """
        Parse SMHI weather data into a DataFrame
        
        Args:
            weather_data: Raw weather data from SMHI API
        """
        try:
            # Extract time series data from SMHI response
            if 'value' not in weather_data:
                logger.error("No value found in weather data")
                return pd.DataFrame()
            
            values = weather_data['value']
            processed_data = []
            
            for entry in values:
                timestamp = entry.get('date')
                value = entry.get('value')
                
                if timestamp and value is not None:
                    processed_data.append({
                        'timestamp': timestamp,
                        'value': value
                    })
            
            df = pd.DataFrame(processed_data)
            
            if not df.empty:
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                logger.info(f"Processed {len(df)} weather records")
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing SMHI data: {e}")
            return pd.DataFrame()
    
    def extract_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract relevant weather features for delay prediction
        
        Args:
            df: Weather DataFrame with raw data
        """
        if df.empty:
            return df
        
        features_df = df.copy()
        
        # Extract hour, day of week, month
        features_df['hour'] = features_df.index.hour
        features_df['day_of_week'] = features_df.index.dayofweek
        features_df['month'] = features_df.index.month
        features_df['is_weekend'] = features_df['day_of_week'].isin([5, 6]).astype(int)
        
        # Create weather severity features based on the 'value' column
        if 'value' in features_df.columns:
            # Determine what type of data this is based on the parameter
            # For now, we'll assume it's precipitation if the values are small (mm)
            # This should be improved with parameter metadata
            
            # Precipitation features
            features_df['precipitation_mm'] = features_df['value']
            features_df['heavy_rain'] = (features_df['precipitation_mm'] > 5).astype(int)
            features_df['moderate_rain'] = ((features_df['precipitation_mm'] > 1) & 
                                           (features_df['precipitation_mm'] <= 5)).astype(int)
            
            # Temperature features (if values are in reasonable range for temperature)
            if features_df['value'].mean() > -50 and features_df['value'].mean() < 50:
                features_df['temperature_c'] = features_df['value']
                features_df['cold_weather'] = (features_df['temperature_c'] < 0).astype(int)
                features_df['freezing_weather'] = (features_df['temperature_c'] < -5).astype(int)
            
            # Wind speed features (if values are in reasonable range for wind)
            if features_df['value'].mean() > 0 and features_df['value'].mean() < 50:
                features_df['wind_speed_ms'] = features_df['value']
                features_df['strong_wind'] = (features_df['wind_speed_ms'] > 10).astype(int)
            
            # Snow depth features (if values are in reasonable range for snow)
            if features_df['value'].mean() >= 0 and features_df['value'].mean() < 10:
                features_df['snow_depth_cm'] = features_df['value'] * 100  # Convert to cm
                features_df['snow_conditions'] = (features_df['snow_depth_cm'] > 5).astype(int)
        
        # Create time-based features
        features_df['rush_hour_morning'] = ((features_df['hour'] >= 7) & 
                                          (features_df['hour'] <= 9)).astype(int)
        features_df['rush_hour_evening'] = ((features_df['hour'] >= 16) & 
                                          (features_df['hour'] <= 18)).astype(int)
        
        # Weather condition score (higher = worse conditions)
        weather_score = 0
        if 'heavy_rain' in features_df.columns:
            weather_score += features_df['heavy_rain'] * 3
        if 'moderate_rain' in features_df.columns:
            weather_score += features_df['moderate_rain'] * 1
        if 'freezing_weather' in features_df.columns:
            weather_score += features_df['freezing_weather'] * 2
        if 'strong_wind' in features_df.columns:
            weather_score += features_df['strong_wind'] * 1
        
        features_df['weather_severity_score'] = weather_score
        
        logger.info(f"Extracted {len(features_df.columns)} weather features")
        return features_df
    
    def create_weather_summary(self, df: pd.DataFrame) -> Dict:
        """
        Create a summary of current weather conditions
        
        Args:
            df: Processed weather DataFrame
        """
        if df.empty:
            return {}
        
        # Get latest weather data
        latest = df.iloc[-1] if len(df) > 0 else df
        
        summary = {
            'timestamp': latest.name.isoformat() if hasattr(latest, 'name') else datetime.now().isoformat(),
            'temperature_c': float(latest.get('temperature_c', 0)),
            'precipitation_mm': float(latest.get('precipitation_mm', 0)),
            'wind_speed_ms': float(latest.get('wind_speed_ms', 0)),
            'weather_severity_score': int(latest.get('weather_severity_score', 0)),
            'is_weekend': bool(latest.get('is_weekend', 0)),
            'rush_hour': bool(latest.get('rush_hour_morning', 0) or latest.get('rush_hour_evening', 0)),
            'conditions': {
                'heavy_rain': bool(latest.get('heavy_rain', 0)),
                'moderate_rain': bool(latest.get('moderate_rain', 0)),
                'freezing_weather': bool(latest.get('freezing_weather', 0)),
                'strong_wind': bool(latest.get('strong_wind', 0))
            }
        }
        
        return summary
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> bool:
        """Save processed weather data"""
        try:
            df.to_csv(filename)
            logger.info(f"Processed weather data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving processed weather data: {e}")
            return False

if __name__ == "__main__":
    # Test the processor
    processor = WeatherProcessor()
    
    # Load sample weather data
    try:
        with open("data/raw/weather_stockholm.json", "r") as f:
            weather_data = json.load(f)
        
        # Process the data
        df = processor.parse_smhi_data(weather_data)
        if not df.empty:
            features_df = processor.extract_weather_features(df)
            processor.save_processed_data(features_df, "data/processed/weather_features.csv")
            
            # Create summary
            summary = processor.create_weather_summary(features_df)
            print("Weather summary:", summary)
        else:
            print("No weather data to process")
            
    except FileNotFoundError:
        print("No weather data file found. Run weather collector first.")
