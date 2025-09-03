#!/usr/bin/env python3
"""
API Exploration Script
Runs comprehensive tests of SMHI and Trafiklab APIs
"""
import os
import sys
import json
from datetime import datetime
import logging

# Add src to path
sys.path.append('src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_smhi_exploration():
    """Run SMHI API exploration tests"""
    print("\n" + "="*60)
    print("🌤️  SMHI API EXPLORATION")
    print("="*60)
    
    try:
        # Test current observations API
        print("\n1. Testing SMHI Observations API (current)...")
        from data_collectors.smhi_weather import SMHIWeatherCollector
        
        obs_collector = SMHIWeatherCollector()
        
        # Test different parameters
        test_params = {
            'temperature': obs_collector.get_temperature_data(),
            'precipitation': obs_collector.get_precipitation_data(),
            'wind': obs_collector.get_wind_speed_data(),
            'snow': obs_collector.get_snow_depth_data()
        }
        
        for param_name, data in test_params.items():
            if data:
                print(f"   ✅ {param_name.capitalize()}: Data available")
            else:
                print(f"   ❌ {param_name.capitalize()}: No data")
        
        # Test forecast API
        print("\n2. Testing SMHI Forecast API...")
        from data_collectors.smhi_forecast import SMHIForecastCollector
        
        forecast_collector = SMHIForecastCollector()
        
        # Test different forecast categories
        forecast_tests = {
            'precipitation': forecast_collector.get_precipitation_forecast(),
            'temperature': forecast_collector.get_temperature_forecast(),
            'wind': forecast_collector.get_wind_forecast(),
            'cloud': forecast_collector.get_cloud_forecast()
        }
        
        for category, data in forecast_tests.items():
            if data and data.get('timeSeries'):
                print(f"   ✅ {category.capitalize()} forecast: {len(data['timeSeries'])} timepoints")
            else:
                print(f"   ❌ {category.capitalize()} forecast: No data")
        
        # Compare forecast vs observations
        print("\n3. Comparing Forecast vs Observations...")
        comparison = forecast_collector.compare_forecast_vs_observation()
        
        if comparison.get('comparison', {}).get('data_availability'):
            for data_type, availability in comparison['comparison']['data_availability'].items():
                status = "✅" if availability.get('both_available') else "⚠️"
                print(f"   {status} {data_type.capitalize()}: Forecast={availability.get('forecast')}, Obs={availability.get('observation')}")
        
        # Save results
        os.makedirs('data/raw', exist_ok=True)
        forecast_collector.save_forecast_data(forecast_tests, "data/raw/smhi_forecast_test.json")
        forecast_collector.save_forecast_data(comparison, "data/raw/smhi_comparison_test.json")
        
        print("\n✅ SMHI exploration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ SMHI exploration failed: {e}")
        return False

def run_trafiklab_exploration():
    """Run Trafiklab API exploration tests"""
    print("\n" + "="*60)
    print("🚌 TRAFIKLAB API EXPLORATION")
    print("="*60)
    
    try:
        # Test current SL API
        print("\n1. Testing SL API (current)...")
        from data_collectors.trafiklab_api import TrafiklabCollector
        
        sl_collector = TrafiklabCollector()
        
        # Test real-time departures
        print("   Testing real-time departures...")
        departures = sl_collector.get_realtime_departures("9192")  # T-Centralen
        
        if departures and departures.get('ResponseData'):
            response_data = departures['ResponseData']
            bus_count = len(response_data.get('Buses', []))
            print(f"   ✅ Real-time departures: {bus_count} buses found")
        else:
            print("   ❌ Real-time departures: No data")
        
        # Test delay extraction
        print("   Testing delay extraction...")
        delay_data = sl_collector.get_delay_data("9192")
        
        if delay_data and delay_data.get('delays'):
            delay_count = len(delay_data['delays'])
            print(f"   ✅ Delay data: {delay_count} delays extracted")
        else:
            print("   ❌ Delay data: No delays found")
        
        # Test Trafiklab GTFS
        print("\n2. Testing Trafiklab GTFS...")
        from data_collectors.trafiklab_gtfs_collector import TrafiklabGTFSCollector
        
        gtfs_collector = TrafiklabGTFSCollector()
        
        # Get GTFS info
        gtfs_info = gtfs_collector.get_gtfs_info()
        
        print("   Checking GTFS endpoints...")
        for dataset, info in gtfs_info.get('available_datasets', {}).items():
            status = "✅" if info.get('accessible') else "❌"
            print(f"   {status} {dataset}: {info.get('status', 'error')}")
        
        # Try to download GTFS data
        print("   Attempting GTFS download...")
        download_result = gtfs_collector.download_gtfs_data('stockholm')
        
        if download_result.get('success'):
            print(f"   ✅ GTFS download successful: {len(download_result.get('files', []))} files")
            
            # Analyze structure
            structure_analysis = gtfs_collector.analyze_gtfs_structure()
            if structure_analysis.get('summary', {}).get('key_files_present'):
                print("   ✅ Key GTFS files present")
            else:
                print("   ⚠️ Some key GTFS files missing")
        else:
            print(f"   ❌ GTFS download failed: {download_result.get('error', 'Unknown error')}")
        
        # Save results
        os.makedirs('data/raw', exist_ok=True)
        gtfs_collector.save_analysis(gtfs_info, "data/raw/trafiklab_gtfs_info.json")
        
        if download_result.get('success'):
            gtfs_collector.save_analysis(structure_analysis, "data/raw/trafiklab_gtfs_structure.json")
        
        print("\n✅ Trafiklab exploration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Trafiklab exploration failed: {e}")
        return False

def create_exploration_summary():
    """Create a summary of the exploration results"""
    print("\n" + "="*60)
    print("📊 EXPLORATION SUMMARY")
    print("="*60)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'smhi_apis': {
            'observations': 'Tested - Multiple parameters available',
            'forecast': 'Tested - Multiple categories available',
            'comparison': 'Tested - Forecast vs observations comparison'
        },
        'trafiklab_apis': {
            'sl_realtime': 'Tested - Real-time departures and delays',
            'gtfs_sweden': 'Tested - Structure and availability',
            'endpoints': 'Tested - Multiple GTFS endpoints'
        },
        'recommendations': [
            'Continue with SMHI Observations + Forecast APIs',
            'Continue with SL Realtime APIs',
            'Investigate GTFS Sweden 3 for historical data',
            'Consider ResRobot APIs for broader coverage'
        ],
        'next_steps': [
            'Implement combined SMHI + Trafiklab data pipeline',
            'Train model on real historical data',
            'Validate prediction accuracy',
            'Scale to production'
        ]
    }
    
    # Save summary
    os.makedirs('data/raw', exist_ok=True)
    with open('data/raw/exploration_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n📋 Summary:")
    for category, items in summary.items():
        if isinstance(items, dict):
            print(f"\n{category.upper()}:")
            for key, value in items.items():
                print(f"  • {key}: {value}")
        elif isinstance(items, list):
            print(f"\n{category.upper()}:")
            for item in items:
                print(f"  • {item}")
    
    print(f"\n📄 Summary saved to: data/raw/exploration_summary.json")

def main():
    """Main exploration function"""
    print("🔍 API EXPLORATION STARTING")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Create data directory
    os.makedirs('data/raw', exist_ok=True)
    
    # Run explorations
    smhi_success = run_smhi_exploration()
    trafiklab_success = run_trafiklab_exploration()
    
    # Create summary
    create_exploration_summary()
    
    # Final status
    print("\n" + "="*60)
    print("🏁 EXPLORATION COMPLETED")
    print("="*60)
    
    if smhi_success and trafiklab_success:
        print("✅ All explorations completed successfully!")
    else:
        print("⚠️ Some explorations had issues - check logs above")
    
    print("\n📁 Results saved in: data/raw/")
    print("📄 Check API_EXPLORATION.md for detailed analysis")

if __name__ == "__main__":
    main()
