#!/usr/bin/env python3
"""
Snabb test för Weather-Based Delay Prediction PoC
Testar alla komponenter utan att starta hela API:en
"""

import sys
import os
from datetime import datetime

# Lägg till src i Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_components():
    """Testa alla komponenter"""
    print("🚀 Snabb test av Weather-Based Delay Prediction PoC")
    print("=" * 50)
    
    # Test 1: Väderdata insamling
    print("\n📋 Test 1: Väderdata insamling")
    print("-" * 30)
    try:
        from data_collectors.smhi_weather import SMHIWeatherCollector
        collector = SMHIWeatherCollector()
        weather_data = collector.get_precipitation_data()
        
        if weather_data and 'timeSeries' in weather_data:
            print("✅ Väderdata insamling: OK")
            print(f"   Antal datapunkter: {len(weather_data['timeSeries'])}")
        else:
            print("❌ Väderdata insamling: FAILED")
            return False
    except Exception as e:
        print(f"❌ Fel vid väderdata insamling: {e}")
        return False
    
    # Test 2: Väderdata bearbetning
    print("\n📋 Test 2: Väderdata bearbetning")
    print("-" * 30)
    try:
        from data_processing.weather_processor import WeatherProcessor
        processor = WeatherProcessor()
        
        df = processor.parse_smhi_data(weather_data)
        if not df.empty:
            features_df = processor.extract_weather_features(df)
            summary = processor.create_weather_summary(features_df)
            
            print("✅ Väderdata bearbetning: OK")
            print(f"   Features extraherade: {len(features_df.columns)}")
            print(f"   Weather severity score: {summary.get('weather_severity_score', 'N/A')}")
        else:
            print("❌ Väderdata bearbetning: FAILED")
            return False
    except Exception as e:
        print(f"❌ Fel vid väderdata bearbetning: {e}")
        return False
    
    # Test 3: ML-modell
    print("\n📋 Test 3: ML-modell")
    print("-" * 30)
    try:
        from models.delay_predictor import DelayPredictor
        predictor = DelayPredictor()
        
        # Skapa träningsdata och träna modellen
        training_data = predictor.create_training_data(None, None)
        metrics = predictor.train(training_data)
        
        if metrics and 'test_r2' in metrics:
            print("✅ ML-modell: OK")
            print(f"   Test R²: {metrics['test_r2']:.3f}")
            print(f"   Test MAE: {metrics['test_mae']:.3f}")
            
            # Testa prediktion
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
            print(f"   Prediktion: {prediction['predicted_delay_minutes']:.1f} min försening")
        else:
            print("❌ ML-modell: FAILED")
            return False
    except Exception as e:
        print(f"❌ Fel vid ML-modell: {e}")
        return False
    
    # Test 4: Trafikdata (mock)
    print("\n📋 Test 4: Trafikdata (mock)")
    print("-" * 30)
    try:
        from data_collectors.trafiklab_api import TrafiklabCollector
        collector = TrafiklabCollector()
        mock_data = collector.create_mock_delay_data()
        
        if mock_data and 'delays' in mock_data:
            print("✅ Trafikdata (mock): OK")
            print(f"   Antal förseningar: {len(mock_data['delays'])}")
        else:
            print("❌ Trafikdata (mock): FAILED")
            return False
    except Exception as e:
        print(f"❌ Fel vid trafikdata: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALLA KOMPONENTER FUNGERAR!")
    print("=" * 50)
    print("\n📝 PoC är redo för användning!")
    print("\nNästa steg:")
    print("1. Kör 'python3 src/api/main.py' för att starta API")
    print("2. Besök http://localhost:8000/docs för API dokumentation")
    print("3. Testa endpoints med curl eller webbläsare")
    print("\nExempel på API-anrop:")
    print("curl http://localhost:8000/weather")
    print("curl -X POST http://localhost:8000/predict \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"temperature_c\": -2, \"precipitation_mm\": 8, \"wind_speed_ms\": 12, \"hour\": 8, \"day_of_week\": 1, \"is_weekend\": 0, \"rush_hour\": 1}'")
    
    return True

if __name__ == "__main__":
    success = test_components()
    sys.exit(0 if success else 1)
