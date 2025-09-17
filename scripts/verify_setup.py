#!/usr/bin/env python3
"""
Environment Verification Script
Verifierar att Python environment är korrekt konfigurerat
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Kontrollera Python version"""
    print("🐍 Python Version Check:")
    version = sys.version_info
    print(f"   Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor in [8, 9, 10]:
        print("   ✅ Python version OK")
        return True
    elif version.major == 3 and version.minor in [11, 12]:
        print("   ⚠️  Python 3.11/3.12 - kan orsaka dependency-konflikter")
        return False
    else:
        print("   ❌ Python version inte kompatibel")
        return False

def check_venv():
    """Kontrollera om vi är i virtual environment"""
    print("\n🔧 Virtual Environment Check:")
    
    # Kontrollera VIRTUAL_ENV environment variable
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"   ✅ VIRTUAL_ENV: {venv_path}")
        return True
    else:
        print("   ❌ VIRTUAL_ENV inte satt - venv inte aktiverat")
        return False

def check_python_path():
    """Kontrollera Python executable path"""
    print("\n📍 Python Path Check:")
    python_path = sys.executable
    print(f"   Python executable: {python_path}")
    
    if 'venv' in python_path:
        print("   ✅ Använder venv Python")
        return True
    else:
        print("   ❌ Använder system Python - venv inte aktiverat")
        return False

def check_dependencies():
    """Kontrollera att viktiga dependencies är installerade"""
    print("\n📦 Dependencies Check:")
    
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'fastapi', 'uvicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - saknas")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_data_files():
    """Kontrollera att data filer finns"""
    print("\n📁 Data Files Check:")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("   ❌ data/ mapp saknas")
        return False
    
    # Kontrollera raw data
    raw_dir = data_dir / "raw"
    if raw_dir.exists():
        games_files = list(raw_dir.glob("games_*.json"))
        if games_files:
            print(f"   ✅ {len(games_files)} games filer hittades")
        else:
            print("   ⚠️  Inga games filer hittades - kör data collection")
    else:
        print("   ❌ data/raw/ mapp saknas")
        return False
    
    # Kontrollera processed data
    processed_dir = data_dir / "processed"
    if processed_dir.exists():
        csv_files = list(processed_dir.glob("games_*.csv"))
        if csv_files:
            print(f"   ✅ {len(csv_files)} processed filer hittades")
        else:
            print("   ⚠️  Inga processed filer hittades - kör ETL pipeline")
    else:
        print("   ❌ data/processed/ mapp saknas")
        return False
    
    return True

def main():
    """Huvudfunktion för verifiering"""
    print("🔍 IGDB Data Engineering - Environment Verification")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_venv(),
        check_python_path(),
        check_dependencies(),
        check_data_files()
    ]
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    
    if all(checks):
        print("🎉 Alla kontroller passerade! Environment är korrekt konfigurerat.")
        print("\n🚀 Du kan nu köra:")
        print("   ./venv/bin/python collect_data.py --games-limit 100")
        print("   ./venv/bin/python -m uvicorn src.api_endpoints.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("❌ Några kontroller misslyckades. Se ovan för detaljer.")
        print("\n🔧 Lösningar:")
        print("   1. Aktivera venv: source venv/bin/activate")
        print("   2. Använd direkt sökväg: ./venv/bin/python [command]")
        print("   3. Installera dependencies: pip install -r requirements.txt")
        print("   4. Kör data collection: ./venv/bin/python collect_data.py --games-limit 100")

if __name__ == "__main__":
    main()
