"""
Trafiklab GTFS Collector
Fetches and analyzes GTFS Sweden 3 data from Trafiklab
"""
import requests
import json
import zipfile
import io
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafiklabGTFSCollector:
    """Collects and analyzes GTFS Sweden 3 data from Trafiklab"""
    
    def __init__(self):
        # Import token manager
        import sys
        sys.path.append('src')
        from utils.api_token_manager import token_manager
        self.token_manager = token_manager
        
        # Get API keys from environment
        self.static_api_key = os.getenv('GTFS_SWEDEN_3_STATIC_DATA_TRAFIKLAB_API_KEY')
        self.realtime_api_key = os.getenv('GTFS_SWEDEN_3_REALTIME_TRAFIKLAB_API_KEY')
        
        if not self.static_api_key:
            raise ValueError("GTFS_SWEDEN_3_STATIC_DATA_TRAFIKLAB_API_KEY not found in environment")
        if not self.realtime_api_key:
            raise ValueError("GTFS_SWEDEN_3_REALTIME_TRAFIKLAB_API_KEY not found in environment")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Weather-Delay-Prediction-PoC/1.0'
        })
        
        # GTFS Sweden 3 endpoints (from actual documentation)
        self.endpoints = {
            'static': 'https://opendata.samtrafiken.se/gtfs-sweden/sweden.zip',
            'realtime_base': 'https://opendata.samtrafiken.se/gtfs-rt-sweden',
            'extra': 'https://opendata.samtrafiken.se/gtfs-sweden/sweden_extra.zip'
        }
        
        # GTFS file structure (from documentation)
        self.gtfs_files = [
            'agency.txt',           # Transportbolag
            'stops.txt',            # Hållplatser
            'routes.txt',           # Linjer
            'trips.txt',            # Resor
            'stop_times.txt',       # Avgångstider
            'calendar.txt',         # Kalender
            'calendar_dates.txt',   # Undantag
            'shapes.txt',           # Rutter (endast Regional/Sweden 3)
            'booking_rules.txt',    # Bokningsregler (endast Regional/Sweden 3)
            'areas.txt',            # Områden (endast Sweden 3)
            'stop_areas.txt'        # Hållplatsområden (endast Sweden 3)
        ]
        
        # Operators covered by GTFS Sweden 3 (from documentation)
        self.operators = {
            'sl': 'SL',
            'ul': 'UL', 
            'sormland': 'Sörmlandstrafiken',
            'otraf': 'Östgötatrafiken',
            'jlt': 'JLT',
            'krono': 'Kronoberg',
            'klt': 'KLT',
            'gotland': 'Gotland',
            'blekinge': 'Blekingetrafiken',
            'skane': 'Skånetrafiken',
            'halland': 'Hallandstrafiken',
            'vt': 'Västtrafik',
            'varm': 'Värmlandstrafik',
            'orebro': 'Örebro',
            'vastmanland': 'Västmanland',
            'dt': 'Dalatrafik',
            'xt': 'X-trafik',
            'dintur': 'Din Tur - Västernorrland',
            'jamtland': 'Jämtland',
            'vasterbotten': 'Västerbotten',
            'norrbotten': 'Norrbotten'
        }
    
    def download_static_data(self, save_path: str = 'data/raw/gtfs') -> Dict:
        """
        Download GTFS Sweden 3 static data
        
        Args:
            save_path: Path to save the data
        """
        # Check if we can make the request
        if not self.token_manager.can_make_request('gtfs_sweden_3_static'):
            return {
                'success': False,
                'error': 'API limit reached for static data'
            }
        
        try:
            os.makedirs(save_path, exist_ok=True)
            
            url = f"{self.endpoints['static']}?key={self.static_api_key}"
            logger.info(f"Downloading GTFS Sweden 3 static data from {url}")
            
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Extract ZIP file
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                extracted_files = []
                for file_name in zip_file.namelist():
                    if file_name.endswith('.txt'):
                        zip_file.extract(file_name, save_path)
                        extracted_files.append(file_name)
                
                logger.info(f"Extracted {len(extracted_files)} GTFS files")
                
                # Record successful request
                self.token_manager.record_request(
                    'gtfs_sweden_3_static',
                    'static_data_download',
                    True,
                    len(response.content)
                )
                
                return {
                    'success': True,
                    'files': extracted_files,
                    'save_path': save_path,
                    'total_size': len(response.content)
                }
                
        except Exception as e:
            logger.error(f"Error downloading GTFS static data: {e}")
            
            # Record failed request
            self.token_manager.record_request(
                'gtfs_sweden_3_static',
                'static_data_download',
                False,
                0
            )
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_realtime_data(self, 
                             operator: str = 'sl',
                             data_type: str = 'ServiceAlerts',
                             save_path: str = 'data/raw/gtfs_rt') -> Dict:
        """
        Download GTFS Sweden 3 realtime data
        
        Args:
            operator: Operator abbreviation (sl, ul, etc.)
            data_type: ServiceAlerts, TripUpdates, or VehiclePositions
            save_path: Path to save the data
        """
        # Check if we can make the request
        if not self.token_manager.can_make_request('gtfs_sweden_3_realtime'):
            return {
                'success': False,
                'error': 'API limit reached for realtime data'
            }
        
        try:
            os.makedirs(save_path, exist_ok=True)
            
            url = f"{self.endpoints['realtime_base']}/{operator}/{data_type}Sweden.pb?key={self.realtime_api_key}"
            logger.info(f"Downloading GTFS realtime data: {operator}/{data_type}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save protobuf file
            filename = f"{operator}_{data_type.lower()}.pb"
            filepath = os.path.join(save_path, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Saved realtime data to {filepath}")
            
            # Record successful request
            self.token_manager.record_request(
                'gtfs_sweden_3_realtime',
                f'{operator}_{data_type}',
                True,
                len(response.content)
            )
            
            return {
                'success': True,
                'operator': operator,
                'data_type': data_type,
                'filepath': filepath,
                'size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"Error downloading realtime data: {e}")
            
            # Record failed request
            self.token_manager.record_request(
                'gtfs_sweden_3_realtime',
                f'{operator}_{data_type}',
                False,
                0
            )
            
            return {
                'success': False,
                'operator': operator,
                'data_type': data_type,
                'error': str(e)
            }
    
    def analyze_static_data(self, data_path: str = 'data/raw/gtfs') -> Dict:
        """
        Analyze the structure of downloaded GTFS static data
        
        Args:
            data_path: Path to GTFS data files
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': {},
            'summary': {},
            'stockholm_data': {}
        }
        
        try:
            # Check which GTFS files exist
            for file_name in self.gtfs_files:
                file_path = os.path.join(data_path, file_name)
                if os.path.exists(file_path):
                    try:
                        # Read first few lines to understand structure
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        if lines:
                            # Parse header
                            header = lines[0].strip().split(',')
                            
                            # Count rows (excluding header)
                            row_count = len(lines) - 1
                            
                            analysis['files_analyzed'][file_name] = {
                                'exists': True,
                                'columns': header,
                                'row_count': row_count,
                                'sample_data': lines[1:3] if len(lines) > 1 else []
                            }
                        else:
                            analysis['files_analyzed'][file_name] = {
                                'exists': True,
                                'columns': [],
                                'row_count': 0,
                                'sample_data': []
                            }
                            
                    except Exception as e:
                        analysis['files_analyzed'][file_name] = {
                            'exists': True,
                            'error': str(e)
                        }
                else:
                    analysis['files_analyzed'][file_name] = {
                        'exists': False
                    }
            
            # Extract Stockholm-specific data
            analysis['stockholm_data'] = self._extract_stockholm_data(data_path)
            
            # Create summary
            existing_files = [f for f, info in analysis['files_analyzed'].items() 
                            if info.get('exists', False)]
            total_rows = sum(info.get('row_count', 0) for info in analysis['files_analyzed'].values())
            
            analysis['summary'] = {
                'total_files': len(existing_files),
                'total_rows': total_rows,
                'key_files_present': all(
                    analysis['files_analyzed'].get(f, {}).get('exists', False)
                    for f in ['stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt']
                ),
                'gtfs_sweden_3_features': {
                    'has_shapes': analysis['files_analyzed'].get('shapes.txt', {}).get('exists', False),
                    'has_booking_rules': analysis['files_analyzed'].get('booking_rules.txt', {}).get('exists', False),
                    'has_areas': analysis['files_analyzed'].get('areas.txt', {}).get('exists', False),
                    'has_stop_areas': analysis['files_analyzed'].get('stop_areas.txt', {}).get('exists', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing GTFS structure: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _extract_stockholm_data(self, data_path: str) -> Dict:
        """Extract Stockholm-specific data from GTFS"""
        stockholm_data = {
            'stops': [],
            'routes': [],
            'summary': {}
        }
        
        try:
            # Read stops data
            stops_path = os.path.join(data_path, 'stops.txt')
            if os.path.exists(stops_path):
                stops_df = pd.read_csv(stops_path)
                
                # Filter for Stockholm area (approximate coordinates)
                stockholm_stops = stops_df[
                    (stops_df['stop_lat'] >= 59.2) & (stops_df['stop_lat'] <= 59.5) &
                    (stops_df['stop_lon'] >= 17.8) & (stops_df['stop_lon'] <= 18.3)
                ]
                
                stockholm_data['stops'] = stockholm_stops.head(10).to_dict('records')
                stockholm_data['summary']['total_stops'] = len(stops_df)
                stockholm_data['summary']['stockholm_stops'] = len(stockholm_stops)
            
            # Read routes data
            routes_path = os.path.join(data_path, 'routes.txt')
            if os.path.exists(routes_path):
                routes_df = pd.read_csv(routes_path)
                
                # Filter for SL routes (agency_id = 'sl')
                sl_routes = routes_df[routes_df['agency_id'] == 'sl']
                
                stockholm_data['routes'] = sl_routes.head(10).to_dict('records')
                stockholm_data['summary']['total_routes'] = len(routes_df)
                stockholm_data['summary']['sl_routes'] = len(sl_routes)
            
        except Exception as e:
            logger.error(f"Error extracting Stockholm data: {e}")
            stockholm_data['error'] = str(e)
        
        return stockholm_data
    
    def save_analysis(self, data: Dict, filename: str) -> bool:
        """Save analysis data to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Analysis saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return False

if __name__ == "__main__":
    # Test the Trafiklab GTFS collector
    print("Testing Trafiklab GTFS Sweden 3 integration...")
    
    try:
        collector = TrafiklabGTFSCollector()
        
        # Show current usage
        collector.token_manager.print_usage_summary()
        
        # Test static data download
        print("\n1. Testing GTFS Sweden 3 static data download...")
        static_result = collector.download_static_data()
        
        if static_result.get('success'):
            print(f"✅ Static data downloaded: {len(static_result.get('files', []))} files")
            
            # Analyze structure
            analysis = collector.analyze_static_data()
            collector.save_analysis(analysis, "data/raw/gtfs_sweden_3_analysis.json")
            print("✅ GTFS structure analyzed and saved")
            
            # Test realtime data
            print("\n2. Testing GTFS Sweden 3 realtime data...")
            realtime_result = collector.download_realtime_data('sl', 'ServiceAlerts')
            
            if realtime_result.get('success'):
                print(f"✅ Realtime data downloaded: {realtime_result['filepath']}")
            else:
                print(f"❌ Realtime data failed: {realtime_result.get('error')}")
        else:
            print(f"❌ Static data download failed: {static_result.get('error')}")
        
        # Show updated usage
        print("\n3. Updated usage summary:")
        collector.token_manager.print_usage_summary()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file contains:")
        print("GTFS_SWEDEN_3_STATIC_DATA_TRAFIKLAB_API_KEY=your_static_key")
        print("GTFS_SWEDEN_3_REALTIME_TRAFIKLAB_API_KEY=your_realtime_key")
    
    print("\nTrafiklab GTFS exploration completed!")
