#!/usr/bin/env python3
"""
Test script för Weather-Based Delay Prediction PoC
Kör alla komponenter för att verifiera att de fungerar
"""

import sys
import os
import json
from datetime import datetime

# Lägg till src i Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_weather_collector():
    """Testa väderdata insamling"""
    print("🧪 Testar väderdata insamling...")
    
    try:
        from data_collectors.smhi_weather import SMHIWeatherCollector
        
        collector = SMHIWeatherCollector()
        weather_data = collector.get_precipitation_data()
        
        if weather_data and 'timeSeries' in weather_data:
            print("✅ Väderdata insamling fungerar!")
            return True
        else:
            print("❌ Väderdata insamling misslyckades")
            return False
            
    except Exception as e:
        print(f"❌ Fel vid väderdata insamling: {e}")
        return False

def test_traffic_collector():
    """Testa trafikdata insamling (mock)"""
    print("🧪 Testar trafikdata insamling...")
    
    try:
        from data_collectors.trafiklab_api import TrafiklabCollector
        
        collector = TrafiklabCollector()
        mock_data = collector.create_mock_delay_data()
        
        if mock_data and 'delays' in mock_data:
            print("✅ Trafikdata insamling fungerar!")
            return True
        else:
            print("❌ Trafikdata insamling misslyckades")
            return False
            
    except Exception as e:
        print(f"❌ Fel vid trafikdata insamling: {e}")
        return False

def test_weather_processor():
    """Testa väderdata bearbetning"""
    print("🧪 Testar väderdata bearbetning...")
    
    try:
        from data_processing.weather_processor import WeatherProcessor
        
        processor = WeatherProcessor()
        
        # Skapa mock väderdata för test
        mock_weather_data = {
            'timeSeries': [
                {
                    'validTime': '2025-01-20T12:00:00Z',
                    'parameters': [
                        {'name': 't', 'values': [5.2]},
                        {'name': 'pmean', 'values': [2.1]},
                        {'name': 'ws', 'values': [8.5]}
                    ]
                },
                {
                    'validTime': '2025-01-20T13:00:00Z',
                    'parameters': [
                        {'name': 't', 'values': [4.8]},
                        {'name': 'pmean', 'values': [3.2]},
                        {'name': 'ws', 'values': [9.1]}
                    ]
                }
            ]
        }
        
        df = processor.parse_smhi_data(mock_weather_data)
        if not df.empty:
            features_df = processor.extract_weather_features(df)
            summary = processor.create_weather_summary(features_df)
            
            if summary and 'weather_severity_score' in summary:
                print("✅ Väderdata bearbetning fungerar!")
                return True
        
        print("❌ Väderdata bearbetning misslyckades")
        return False
        
    except Exception as e:
        print(f"❌ Fel vid väderdata bearbetning: {e}")
        return False

def test_delay_predictor():
    """Testa försening prediktion"""
    print("🧪 Testar försening prediktion...")
    
    try:
        from models.delay_predictor import DelayPredictor
        
        predictor = DelayPredictor()
        
        # Skapa träningsdata och träna modellen
        training_data = predictor.create_training_data(None, None)
        metrics = predictor.train(training_data)
        
        if metrics and 'test_r2' in metrics:
            print(f"✅ Modell tränad! Test R²: {metrics['test_r2']:.3f}")
            
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
            
            if prediction and 'predicted_delay_minutes' in prediction:
                print(f"✅ Prediktion fungerar! Försening: {prediction['predicted_delay_minutes']:.1f} min")
                return True
        
        print("❌ Försening prediktion misslyckades")
        return False
        
    except Exception as e:
        print(f"❌ Fel vid försening prediktion: {e}")
        return False

def test_api():
    """Testa API (endast om FastAPI är tillgängligt)"""
    print("🧪 Testar API...")
    
    try:
        import requests
        import subprocess
        import time
        
        # Starta API i bakgrunden
        print("   Startar API...")
        process = subprocess.Popen([
            sys.executable, "src/api/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Vänta lite för att API ska starta
        time.sleep(3)
        
        try:
            # Testa health endpoint
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API health check fungerar!")
                
                # Testa prediktion endpoint
                test_data = {
                    "temperature_c": -2,
                    "precipitation_mm": 8,
                    "wind_speed_ms": 12,
                    "hour": 8,
                    "day_of_week": 1,
                    "is_weekend": 0,
                    "rush_hour": 1
                }
                
                response = requests.post(
                    "http://localhost:8000/predict",
                    json=test_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ API prediktion fungerar! Försening: {result['predicted_delay_minutes']:.1f} min")
                    return True
                else:
                    print(f"❌ API prediktion misslyckades: {response.status_code}")
                    return False
            else:
                print(f"❌ API health check misslyckades: {response.status_code}")
                return False
                
        finally:
            # Stoppa API process
            process.terminate()
            process.wait()
            
    except Exception as e:
        print(f"❌ Fel vid API test: {e}")
        return False

def main():
    """Huvudfunktion för att köra alla tester"""
    print("🚀 Startar Weather-Based Delay Prediction PoC tester")
    print("=" * 50)
    
    tests = [
        ("Väderdata insamling", test_weather_collector),
        ("Trafikdata insamling", test_traffic_collector),
        ("Väderdata bearbetning", test_weather_processor),
        ("Försening prediktion", test_delay_predictor),
        ("API", test_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Oväntat fel i {test_name}: {e}")
            results.append((test_name, False))
    
    # Sammanfattning
    print("\n" + "=" * 50)
    print("📊 TEST SAMMANFATTNING")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Resultat: {passed}/{total} tester godkända")
    
    if passed == total:
        print("🎉 Alla tester godkända! PoC är redo att användas.")
        print("\n📝 Nästa steg:")
        print("1. Kör 'python src/api/main.py' för att starta API")
        print("2. Besök http://localhost:8000/docs för API dokumentation")
        print("3. Testa endpoints med curl eller webbläsare")
    else:
        print("⚠️  Vissa tester misslyckades. Kontrollera felmeddelanden ovan.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
