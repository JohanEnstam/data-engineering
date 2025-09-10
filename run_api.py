#!/usr/bin/env python3
"""
Entry point for the IGDB Game Recommendation API
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now import and run the API
from api_endpoints.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting IGDB Game Recommendation API...")
    print("📊 Budget monitoring enabled")
    print("🌐 API available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("💰 Budget endpoints at: http://localhost:8000/api/budget/")
    
    uvicorn.run(
        "api_endpoints.main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )