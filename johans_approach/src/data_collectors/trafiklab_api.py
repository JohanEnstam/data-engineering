"""
Trafiklab API Data Collector
Fetches public transport data from Trafiklab APIs
"""
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafiklabCollector:
    """
    Collect public transport data from Trafiklab APIs
    Focus on SL inner city bus traffic for PoC
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Trafiklab collector
        
        Args:
            api_key: Trafiklab API key (optional for demo endpoints)
        """
        self.api_key = api_key or "demo"  # Use demo key if none provided
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Weather-Delay-Prediction-PoC/1.0'
        })
        
        # SL API endpoints
        self.base_url = "https://api.sl.se/api2"
        
        # Common Stockholm inner city bus stops for PoC
        self.inner_city_stops = {
            "9192": "T-Centralen",  # Central station
            "9193": "Gamla Stan",   # Old Town
            "9194": "Slussen",      # Slussen
            "9195": "Mariatorget",  # Mariatorget
            "9196": "Zinkensdamm",  # Zinkensdamm
            "9197": "Hornstull",    # Hornstull
            "9198": "Liljeholmen",  # Liljeholmen
        }
    
    def get_realtime_departures(self, 
                               site_id: str = "9192", 
                               time_window: int = 60) -> Dict:
        """
        Get real-time departures from SL API
        
        Args:
            site_id: Stop ID
            time_window: Time window in minutes
        """
        try:
            url = f"{self.base_url}/realtimedeparturesV4.json"
            params = {
                'key': self.api_key,
                'siteid': site_id,
                'timewindow': time_window
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched real-time departures for stop {site_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching real-time departures: {e}")
            return {}
    
    def get_journey_planner_data(self, 
                                origin: str = "9192", 
                                destination: str = "9193",
                                time: str = "12:00") -> Dict:
        """
        Get journey planner data from SL API
        
        Args:
            origin: Origin stop ID
            destination: Destination stop ID
            time: Departure time (HH:MM)
        """
        try:
            url = f"{self.base_url}/travelplannerV3_1/trip.json"
            params = {
                'key': self.api_key,
                'originExtId': origin,
                'destExtId': destination,
                'time': time
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched journey planner data from {origin} to {destination}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching journey planner data: {e}")
            return {}
    
    def get_delay_data(self, site_id: str = "9192") -> Dict:
        """
        Extract delay information from real-time departures
        
        Args:
            site_id: Stop ID
        """
        try:
            # Get real-time departures
            departures = self.get_realtime_departures(site_id)
            
            if not departures or 'ResponseData' not in departures:
                return {}
            
            response_data = departures['ResponseData']
            delay_data = {
                'stop_id': site_id,
                'stop_name': self.inner_city_stops.get(site_id, f"Stop {site_id}"),
                'timestamp': datetime.now().isoformat(),
                'delays': []
            }
            
            # Process bus departures
            if 'Buses' in response_data:
                for bus in response_data['Buses']:
                    if 'ExpectedDateTime' in bus and 'TimeTabledDateTime' in bus:
                        expected = datetime.fromisoformat(bus['ExpectedDateTime'].replace('Z', '+00:00'))
                        scheduled = datetime.fromisoformat(bus['TimeTabledDateTime'].replace('Z', '+00:00'))
                        
                        delay_minutes = (expected - scheduled).total_seconds() / 60
                        
                        delay_info = {
                            'line': bus.get('LineNumber', 'Unknown'),
                            'destination': bus.get('Destination', 'Unknown'),
                            'scheduled_time': scheduled.isoformat(),
                            'expected_time': expected.isoformat(),
                            'delay_minutes': round(delay_minutes, 1),
                            'is_delayed': delay_minutes > 0
                        }
                        
                        delay_data['delays'].append(delay_info)
            
            logger.info(f"Extracted delay data for stop {site_id}: {len(delay_data['delays'])} departures")
            return delay_data
            
        except Exception as e:
            logger.error(f"Error extracting delay data: {e}")
            return {}
    
    def get_multiple_stops_delay_data(self, stop_ids: List[str] = None) -> Dict:
        """
        Get delay data from multiple stops
        
        Args:
            stop_ids: List of stop IDs to check
        """
        if stop_ids is None:
            stop_ids = list(self.inner_city_stops.keys())[:3]  # Use first 3 stops for PoC
        
        all_delays = {
            'timestamp': datetime.now().isoformat(),
            'stops': []
        }
        
        for stop_id in stop_ids:
            delay_data = self.get_delay_data(stop_id)
            if delay_data:
                all_delays['stops'].append(delay_data)
        
        logger.info(f"Collected delay data from {len(all_delays['stops'])} stops")
        return all_delays
    
    def save_delay_data(self, data: Dict, filename: str) -> bool:
        """
        Save delay data to file
        
        Args:
            data: Delay data to save
            filename: Output filename
        """
        try:
            os.makedirs('data/raw', exist_ok=True)
            filepath = f"data/raw/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Delay data saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving delay data: {e}")
            return False
    
    def create_mock_delay_data(self) -> Dict:
        """
        Create mock delay data for testing when API is not available
        """
        mock_data = {
            'timestamp': datetime.now().isoformat(),
            'stops': []
        }
        
        for stop_id, stop_name in list(self.inner_city_stops.items())[:3]:
            stop_data = {
                'stop_id': stop_id,
                'stop_name': stop_name,
                'delays': []
            }
            
            # Create some mock delays
            for i in range(3):
                delay_info = {
                    'line': f"Bus {100 + i}",
                    'destination': f"Destination {i + 1}",
                    'scheduled_time': (datetime.now() + timedelta(minutes=10 + i*5)).isoformat(),
                    'expected_time': (datetime.now() + timedelta(minutes=12 + i*5)).isoformat(),
                    'delay_minutes': round(2 + i*0.5, 1),
                    'is_delayed': True
                }
                stop_data['delays'].append(delay_info)
            
            mock_data['stops'].append(stop_data)
        
        return mock_data

if __name__ == "__main__":
    # Test the Trafiklab collector
    collector = TrafiklabCollector()
    
    print("Testing Trafiklab API integration...")
    
    # Try to get real data first
    try:
        delay_data = collector.get_multiple_stops_delay_data()
        if delay_data and delay_data.get('stops'):
            print("✅ Successfully fetched real delay data from Trafiklab API")
            collector.save_delay_data(delay_data, "delays_sl.json")
        else:
            print("⚠️ No real data available, using mock data")
            delay_data = collector.create_mock_delay_data()
            collector.save_delay_data(delay_data, "delays_mock.json")
    except Exception as e:
        print(f"❌ Error fetching real data: {e}")
        print("Using mock data instead")
        delay_data = collector.create_mock_delay_data()
        collector.save_delay_data(delay_data, "delays_mock.json")
    
    print("Delay data collection completed!")
