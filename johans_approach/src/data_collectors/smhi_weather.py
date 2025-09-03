"""
SMHI Weather Data Collector
Fetches weather data from SMHI Open Data API
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMHIWeatherCollector:
    """Collects weather data from SMHI API"""
    
    def __init__(self):
        self.base_url = "https://opendata.smhi.se/ws/rest"
        self.session = requests.Session()
    
    def get_weather_stations(self) -> List[Dict]:
        """Get available weather stations"""
        url = f"{self.base_url}/stations"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather stations: {e}")
            return []
    
    def get_weather_data(self, 
                        lat: float = 59.3293, 
                        lon: float = 18.0686,
                        parameter: str = "7",  # Precipitation amount (1 hour)
                        version: str = "latest") -> Dict:
        """
        Fetch weather data from SMHI observations API
        
        Args:
            lat: Latitude
            lon: Longitude  
            parameter: Weather parameter ID (7=precipitation, 1=temperature, 8=snow depth)
            version: API version
        """
        try:
            # First get the parameter info
            param_url = f"https://opendata-download-metobs.smhi.se/api/version/{version}/parameter/{parameter}.json"
            param_response = self.session.get(param_url)
            param_response.raise_for_status()
            param_data = param_response.json()
            
            # Find the closest active station to our coordinates
            closest_station = None
            min_distance = float('inf')
            
            for station in param_data.get('station', []):
                # Only consider active stations
                if not station.get('active', False):
                    continue
                    
                station_lat = station.get('latitude', 0)
                station_lon = station.get('longitude', 0)
                
                # Calculate distance (simple euclidean for PoC)
                distance = ((station_lat - lat) ** 2 + (station_lon - lon) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_station = station
            
            if not closest_station:
                logger.error("No active stations found")
                return {}
            
            station_id = closest_station['key']
            logger.info(f"Using station {station_id} ({closest_station.get('name', 'Unknown')})")
            
            # Get the latest period for this station
            station_url = f"https://opendata-download-metobs.smhi.se/api/version/{version}/parameter/{parameter}/station/{station_id}.json"
            station_response = self.session.get(station_url)
            station_response.raise_for_status()
            station_data = station_response.json()
            
            if not station_data.get('period'):
                logger.error("No periods found for station")
                return {}
            
            # For PoC, use latest-day period to get recent data
            period_id = "latest-day"
            logger.info(f"Using period: {period_id}")
            
            # Get the actual weather data
            data_url = f"https://opendata-download-metobs.smhi.se/api/version/{version}/parameter/{parameter}/station/{station_id}/period/{period_id}/data.json"
            data_response = self.session.get(data_url)
            data_response.raise_for_status()
            weather_data = data_response.json()
            
            logger.info(f"Fetched weather data for station {station_id}, parameter {parameter}")
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {}
    
    def create_mock_weather_data(self, lat: float, lon: float) -> Dict:
        """
        Create mock weather data for PoC testing
        """
        from datetime import datetime, timedelta
        import random
        
        now = datetime.now()
        time_series = []
        
        # Create 24 hours of mock data
        for i in range(24):
            timestamp = now + timedelta(hours=i)
            
            # Generate realistic weather data
            temp = random.uniform(-5, 15)  # Temperature between -5 and 15°C
            precip = random.uniform(0, 10)  # Precipitation 0-10mm
            wind = random.uniform(2, 15)    # Wind speed 2-15 m/s
            
            time_series.append({
                'validTime': timestamp.isoformat(),
                'parameters': [
                    {'name': 't', 'values': [round(temp, 1)]},
                    {'name': 'pmean', 'values': [round(precip, 1)]},
                    {'name': 'ws', 'values': [round(wind, 1)]}
                ]
            })
        
        return {
            'approvedTime': now.isoformat(),
            'referenceTime': now.isoformat(),
            'timeSeries': time_series,
            'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            }
        }
    
    def get_temperature_data(self, 
                           lat: float = 59.3293, 
                           lon: float = 18.0686) -> Dict:
        """Get temperature data (parameter 1: momentanvärde, 1 gång/tim)"""
        return self.get_weather_data(lat, lon, parameter="1", version="latest")
    
    def get_precipitation_data(self, 
                             lat: float = 59.3293, 
                             lon: float = 18.0686) -> Dict:
        """Get precipitation data (parameter 7: summa 1 timme, 1 gång/tim)"""
        return self.get_weather_data(lat, lon, parameter="7", version="latest")
    
    def get_snow_depth_data(self, 
                           lat: float = 59.3293, 
                           lon: float = 18.0686) -> Dict:
        """Get snow depth data (parameter 8: momentanvärde, 1 gång/dygn, kl 06)"""
        return self.get_weather_data(lat, lon, parameter="8", version="latest")
    
    def get_wind_speed_data(self, 
                           lat: float = 59.3293, 
                           lon: float = 18.0686) -> Dict:
        """Get wind speed data (parameter 4: medelvärde 10 min, 1 gång/tim)"""
        return self.get_weather_data(lat, lon, parameter="4", version="latest")
    
    def save_weather_data(self, data: Dict, filename: str) -> bool:
        """Save weather data to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Weather data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving weather data: {e}")
            return False

if __name__ == "__main__":
    # Test the collector
    collector = SMHIWeatherCollector()
    
    # Test with Stockholm coordinates
    weather_data = collector.get_precipitation_data()
    if weather_data:
        collector.save_weather_data(weather_data, "data/raw/weather_stockholm.json")
        print("Weather data collected successfully!")
    else:
        print("Failed to collect weather data")
