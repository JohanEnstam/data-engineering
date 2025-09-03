"""
Main API for Weather-Based Delay Prediction
Combines weather data collection, processing, and ML prediction
"""
import os
import json
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collectors.smhi_weather import SMHIWeatherCollector
from data_collectors.trafiklab_api import TrafiklabCollector
from data_processing.weather_processor import WeatherProcessor
from models.delay_predictor import DelayPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Weather-Based Delay Prediction API",
    description="Predicts public transport delays based on weather conditions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
weather_collector = SMHIWeatherCollector()
traffic_collector = TrafiklabCollector()
weather_processor = WeatherProcessor()
delay_predictor = DelayPredictor()

# Pydantic models for API
class WeatherRequest(BaseModel):
    lat: float = 59.3293
    lon: float = 18.0686
    include_traffic: bool = False

class PredictionRequest(BaseModel):
    temperature_c: float
    precipitation_mm: float
    wind_speed_ms: float
    hour: int
    day_of_week: int
    is_weekend: int = 0
    rush_hour: int = 0

class PredictionResponse(BaseModel):
    predicted_delay_minutes: float
    confidence: float
    weather_severity: int
    timestamp: str
    weather_summary: Dict

@app.get("/")
def welcome():
    """Welcome endpoint"""
    return {
        "service": "Weather-Based Delay Prediction API",
        "version": "1.0.0",
        "description": "Predicts public transport delays using weather data",
        "endpoints": {
            "health": "/health",
            "weather": "/weather",
            "predict": "/predict",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "weather_collector": "ready",
            "traffic_collector": "ready", 
            "weather_processor": "ready",
            "delay_predictor": "ready" if delay_predictor.is_trained else "not_trained"
        }
    }

@app.get("/weather")
def get_current_weather(lat: float = 59.3293, lon: float = 18.0686):
    """Get current weather data for specified coordinates"""
    try:
        # Fetch weather data
        weather_data = weather_collector.get_precipitation_data(lat, lon)
        
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")
        
        # Process weather data
        df = weather_processor.parse_smhi_data(weather_data)
        if df.empty:
            raise HTTPException(status_code=500, detail="Failed to process weather data")
        
        features_df = weather_processor.extract_weather_features(df)
        weather_summary = weather_processor.create_weather_summary(features_df)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "weather_summary": weather_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict_delay(request: PredictionRequest):
    """Predict delay based on weather features"""
    try:
        # Prepare weather features
        weather_features = {
            'temperature_c': request.temperature_c,
            'precipitation_mm': request.precipitation_mm,
            'wind_speed_ms': request.wind_speed_ms,
            'weather_severity_score': 0,  # Will be calculated
            'hour': request.hour,
            'day_of_week': request.day_of_week,
            'is_weekend': request.is_weekend,
            'rush_hour': request.rush_hour
        }
        
        # Calculate weather severity score
        weather_score = 0
        if request.precipitation_mm > 5:
            weather_score += 3
        elif request.precipitation_mm > 1:
            weather_score += 1
        if request.temperature_c < -5:
            weather_score += 2
        elif request.temperature_c < 0:
            weather_score += 1
        if request.wind_speed_ms > 10:
            weather_score += 1
        
        weather_features['weather_severity_score'] = weather_score
        
        # Make prediction
        prediction = delay_predictor.predict_delay(weather_features)
        
        # Create weather summary
        weather_summary = {
            'temperature_c': request.temperature_c,
            'precipitation_mm': request.precipitation_mm,
            'wind_speed_ms': request.wind_speed_ms,
            'weather_severity_score': weather_score,
            'conditions': {
                'heavy_rain': request.precipitation_mm > 5,
                'moderate_rain': 1 < request.precipitation_mm <= 5,
                'freezing_weather': request.temperature_c < -5,
                'strong_wind': request.wind_speed_ms > 10
            }
        }
        
        return PredictionResponse(
            predicted_delay_minutes=prediction['predicted_delay_minutes'],
            confidence=prediction['confidence'],
            weather_severity=weather_score,
            timestamp=prediction['timestamp'],
            weather_summary=weather_summary
        )
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/weather")
def predict_from_weather(lat: float = 59.3293, lon: float = 18.0686):
    """Predict delay using current weather data"""
    try:
        # Get current weather
        weather_data = weather_collector.get_precipitation_data(lat, lon)
        
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")
        
        # Process weather data
        df = weather_processor.parse_smhi_data(weather_data)
        if df.empty:
            raise HTTPException(status_code=500, detail="Failed to process weather data")
        
        features_df = weather_processor.extract_weather_features(df)
        weather_summary = weather_processor.create_weather_summary(features_df)
        
        # Prepare features for prediction
        weather_features = {
            'temperature_c': weather_summary.get('temperature_c', 0),
            'precipitation_mm': weather_summary.get('precipitation_mm', 0),
            'wind_speed_ms': weather_summary.get('wind_speed_ms', 0),
            'weather_severity_score': weather_summary.get('weather_severity_score', 0),
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_weekend': int(datetime.now().weekday() in [5, 6]),
            'rush_hour': int(weather_summary.get('rush_hour', False))
        }
        
        # Make prediction
        prediction = delay_predictor.predict_delay(weather_features)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "prediction": prediction,
            "weather_summary": weather_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting from weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
def train_model():
    """Train the delay prediction model"""
    try:
        # Create synthetic training data
        training_data = delay_predictor.create_training_data(None, None)
        
        # Train model
        metrics = delay_predictor.train(training_data)
        
        # Save model
        delay_predictor.save_model("data/models/delay_predictor.pkl")
        
        return {
            "message": "Model trained successfully",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load-model")
def load_model():
    """Load a pre-trained model"""
    try:
        success = delay_predictor.load_model("data/models/delay_predictor.pkl")
        
        if success:
            return {
                "message": "Model loaded successfully",
                "is_trained": delay_predictor.is_trained,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load model")
            
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
