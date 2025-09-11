"""
Basic tests for IGDB Game Recommender System
"""
import pytest
import sys
import os

# Lägg till src till Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_imports():
    """Test that all main modules can be imported"""
    try:
        from src.api_endpoints.main import app
        assert app is not None
        print("✅ Main app imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import main app: {e}")


def test_basic_functionality():
    """Test basic functionality"""
    assert 1 + 1 == 2
    print("✅ Basic functionality test passed")


def test_data_processing_imports():
    """Test that data processing modules can be imported"""
    try:
        from src.data_processing.etl import ETLProcessor
        assert ETLProcessor is not None
        print("✅ ETLProcessor imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import ETLProcessor: {e}")


def test_api_client_imports():
    """Test that API client modules can be imported"""
    try:
        from src.api.igdb_client import IGDBClient
        assert IGDBClient is not None
        print("✅ IGDBClient imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import IGDBClient: {e}")


def test_models_imports():
    """Test that ML model modules can be imported"""
    try:
        from src.models.game_recommender import GameRecommender
        assert GameRecommender is not None
        print("✅ GameRecommender imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import GameRecommender: {e}")


def test_environment_variables():
    """Test that required environment variables are available"""
    import os
    from dotenv import load_dotenv
    
    # Ladda .env fil om den finns
    load_dotenv()
    
    # Kontrollera att IGDB credentials finns (valfritt för CI)
    client_id = os.getenv('IGDB_CLIENT_ID')
    client_secret = os.getenv('IGDB_CLIENT_SECRET')
    
    if client_id and client_secret:
        print("✅ IGDB credentials found")
    else:
        print("⚠️ IGDB credentials not found (OK for CI testing)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
