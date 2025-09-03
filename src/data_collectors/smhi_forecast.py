"""
SMHI Forecast API Data Collector
Fetches weather forecast data from SMHI Forecast API
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMHIForecastCollector:
    """Collects weather forecast data from SMHI Forecast API"""
    
    def __init__(self):
        self.base_url = "https://opendata-download-metfcst.smhi.se/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Weather-Delay-Prediction-PoC/1.0'
        })
    
    def get_forecast_categories(self) -> List[Dict]:
        """Get available forecast categories"""
        try:
            url = f"{self.base_url}/category/pmp3g/version/2/geotype/point"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching forecast categories: {e}")
            return []
    
    def get_forecast_data(self, 
                         lat: float = 59.3293, 
                         lon: float = 18.0686,
                         category: str = "pmp3g",
                         version: str = "2") -> Dict:
        """
        Fetch weather forecast data from SMHI Forecast API
        
        Args:
            lat: Latitude
            lon: Longitude
            category: Forecast category (pmp3g = precipitation, t = temperature, etc.)
            version: API version
        """
        try:
            # Get forecast data for specific coordinates
            url = f"{self.base_url}/category/{category}/version/{version}/geotype/point/lon/{lon}/lat/{lat}/data.json"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            forecast_data = response.json()
            logger.info(f"Fetched forecast data for lat={lat}, lon={lon}, category={category}")
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error fetching forecast data: {e}")
            return {}
    
    def get_precipitation_forecast(self, 
                                 lat: float = 59.3293, 
                                 lon: float = 18.0686) -> Dict:
        """Get precipitation forecast (pmp3g category)"""
        return self.get_forecast_data(lat, lon, category="pmp3g")
    
    def get_temperature_forecast(self, 
                               lat: float = 59.3293, 
                               lon: float = 18.0686) -> Dict:
        """Get temperature forecast (t category)"""
        return self.get_forecast_data(lat, lon, category="t")
    
    def get_wind_forecast(self, 
                        lat: float = 59.3293, 
                        lon: float = 18.0686) -> Dict:
        """Get wind forecast (ws category)"""
        return self.get_forecast_data(lat, lon, category="ws")
    
    def get_cloud_forecast(self, 
                         lat: float = 59.3293, 
                         lon: float = 18.0686) -> Dict:
        """Get cloud forecast (tcc category)"""
        return self.get_forecast_data(lat, lon, category="tcc")
    
    def compare_forecast_vs_observation(self, 
                                      lat: float = 59.3293, 
                                      lon: float = 18.0686) -> Dict:
        """
        Compare forecast data with observation data
        """
        from .smhi_weather import SMHIWeatherCollector
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'location': {'lat': lat, 'lon': lon},
            'forecast': {},
            'observation': {},
            'comparison': {}
        }
        
        # Get forecast data
        forecast_collector = SMHIForecastCollector()
        comparison['forecast'] = {
            'precipitation': forecast_collector.get_precipitation_forecast(lat, lon),
            'temperature': forecast_collector.get_temperature_forecast(lat, lon),
            'wind': forecast_collector.get_wind_forecast(lat, lon)
        }
        
        # Get observation data
        obs_collector = SMHIWeatherCollector()
        comparison['observation'] = {
            'precipitation': obs_collector.get_precipitation_data(lat, lon),
            'temperature': obs_collector.get_temperature_data(lat, lon),
            'wind': obs_collector.get_wind_speed_data(lat, lon)
        }
        
        # Simple comparison analysis
        comparison['comparison'] = self._analyze_comparison(comparison['forecast'], comparison['observation'])
        
        return comparison
    
    def _analyze_comparison(self, forecast: Dict, observation: Dict) -> Dict:
        """Analyze forecast vs observation data"""
        analysis = {
            'data_availability': {},
            'quality_notes': []
        }
        
        # Check data availability
        for data_type in ['precipitation', 'temperature', 'wind']:
            forecast_available = bool(forecast.get(data_type, {}).get('timeSeries'))
            observation_available = bool(observation.get(data_type, {}).get('value'))
            
            analysis['data_availability'][data_type] = {
                'forecast': forecast_available,
                'observation': observation_available,
                'both_available': forecast_available and observation_available
            }
        
        # Add quality notes
        if not any(analysis['data_availability'][dt]['both_available'] for dt in analysis['data_availability']):
            analysis['quality_notes'].append("No overlapping data for comparison")
        
        return analysis
    
    def save_forecast_data(self, data: Dict, filename: str) -> bool:
        """Save forecast data to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Forecast data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving forecast data: {e}")
            return False

if __name__ == "__main__":
    # Test the forecast collector
    collector = SMHIForecastCollector()
    
    print("Testing SMHI Forecast API...")
    
    # Test with Stockholm coordinates
    lat, lon = 59.3293, 18.0686
    
    # Get different forecast types
    forecast_data = {
        'precipitation': collector.get_precipitation_forecast(lat, lon),
        'temperature': collector.get_temperature_forecast(lat, lon),
        'wind': collector.get_wind_forecast(lat, lon),
        'cloud': collector.get_cloud_forecast(lat, lon)
    }
    
    # Save forecast data
    collector.save_forecast_data(forecast_data, "data/raw/weather_forecast_stockholm.json")
    
    # Compare with observations
    comparison = collector.compare_forecast_vs_observation(lat, lon)
    collector.save_forecast_data(comparison, "data/raw/forecast_vs_observation_comparison.json")
    
    print("Forecast data collection completed!")
    print(f"Data saved to data/raw/weather_forecast_stockholm.json")
    print(f"Comparison saved to data/raw/forecast_vs_observation_comparison.json")
