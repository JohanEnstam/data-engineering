#!/usr/bin/env python3
"""
Simple FastAPI server for the IGDB Game Recommendation System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pathlib import Path
from typing import List, Dict, Any

app = FastAPI(
    title="IGDB Game Recommendation API",
    description="API for IGDB game data and recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DATA_DIR = Path(__file__).parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"

def load_games_data() -> List[Dict[str, Any]]:
    """Load games data from the processed JSON file"""
    try:
        # Find the most recent games file
        games_files = list(PROCESSED_DIR.glob("games_*.json"))
        if not games_files:
            print("No games data files found")
            return []
        
        latest_file = max(games_files, key=lambda f: f.stat().st_mtime)
        print(f"Loading games from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            games_data = json.load(f)
        
        return games_data
    except Exception as e:
        print(f"Error loading games data: {e}")
        return []

def load_data_quality_report() -> Dict[str, Any]:
    """Load data quality report from the validation report"""
    try:
        # Find the most recent validation report
        report_files = list(PROCESSED_DIR.glob("validation_report_*.txt"))
        if not report_files:
            return None
        
        latest_file = max(report_files, key=lambda f: f.stat().st_mtime)
        print(f"Loading validation report from: {latest_file}")
        
        # Simple parsing of the validation report
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic information
        lines = content.split('\n')
        total_games = 0
        validation_status = "UNKNOWN"
        issues = []
        
        for line in lines:
            if line.startswith("Total spel:"):
                total_games = int(line.split(":")[1].strip())
            elif line.startswith("Validation status:"):
                validation_status = line.split(":")[1].strip()
            elif line.startswith("  - Kolumner med >50% missing data:"):
                issues.append(line.strip())
        
        return {
            "total_games": total_games,
            "validation_status": validation_status,
            "issues": issues,
            "statistics": {
                "rating": {"min": None, "max": None, "mean": None, "std": None},
                "release_year": {"min": None, "max": None, "mean": None},
                "genres": {"unique_genres": 0, "games_without_genres": 0},
                "themes": {"unique_themes": 0, "games_without_themes": 0},
                "platforms": {"unique_platforms": 0, "games_without_platforms": 0}
            },
            "feature_statistics": {
                "genre_features": {"total_features": 0, "games_without_genres": 0},
                "theme_features": {"total_features": 0, "games_without_themes": 0},
                "platform_features": {"total_features": 0, "games_without_platforms": 0}
            }
        }
    except Exception as e:
        print(f"Error loading data quality report: {e}")
        return None

def load_budget_info() -> Dict[str, Any]:
    """Load budget information (mock data for now)"""
    return {
        "total_credits": 300,
        "used_credits": 45,
        "remaining_credits": 255,
        "monthly_estimate": 85,
        "services": {
            "bigquery": 15,
            "cloud_run": 25,
            "vertex_ai": 0,
            "cloud_storage": 5
        }
    }

@app.get("/")
async def root():
    return {"message": "IGDB Game Recommendation API", "version": "1.0.0"}

@app.get("/api/games")
async def get_games():
    """Get all games from the collection"""
    games = load_games_data()
    if not games:
        raise HTTPException(status_code=404, detail="No games data found")
    return games

@app.get("/api/games/{game_id}")
async def get_game(game_id: int):
    """Get a specific game by ID"""
    games = load_games_data()
    game = next((g for g in games if g["id"] == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.get("/api/games/search")
async def search_games(q: str = "", limit: int = 10):
    """Search games by name or summary"""
    games = load_games_data()
    if not games:
        raise HTTPException(status_code=404, detail="No games data found")
    
    if not q:
        return games[:limit]
    
    # Simple text search
    query_lower = q.lower()
    filtered_games = [
        game for game in games
        if query_lower in game.get("name", "").lower() or 
           query_lower in game.get("summary", "").lower()
    ]
    
    return filtered_games[:limit]

@app.get("/api/data-quality")
async def get_data_quality():
    """Get data quality report"""
    report = load_data_quality_report()
    if not report:
        raise HTTPException(status_code=404, detail="No data quality report found")
    return report

@app.get("/api/budget")
async def get_budget():
    """Get budget information"""
    return load_budget_info()

@app.get("/api/recommendations/{game_id}")
async def get_recommendations(game_id: int, limit: int = 5):
    """Get game recommendations based on a game ID"""
    games = load_games_data()
    if not games:
        raise HTTPException(status_code=404, detail="No games data found")
    
    # Find the target game
    target_game = next((g for g in games if g["id"] == game_id), None)
    if not target_game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Simple content-based filtering based on genres and themes
    recommendations = []
    target_genres = set(target_game.get("genres", []))
    target_themes = set(target_game.get("themes", []))
    
    for game in games:
        if game["id"] == game_id:
            continue
        
        # Calculate similarity score
        game_genres = set(game.get("genres", []))
        game_themes = set(game.get("themes", []))
        
        genre_similarity = len(target_genres.intersection(game_genres)) / max(len(target_genres), 1)
        theme_similarity = len(target_themes.intersection(game_themes)) / max(len(target_themes), 1)
        
        # Weighted similarity score
        similarity_score = (genre_similarity * 0.7) + (theme_similarity * 0.3)
        
        if similarity_score > 0:
            recommendations.append({
                "game": game,
                "similarity_score": similarity_score,
                "reasons": [
                    f"Shares {len(target_genres.intersection(game_genres))} genres",
                    f"Shares {len(target_themes.intersection(game_themes))} themes"
                ]
            })
    
    # Sort by similarity score and return top recommendations
    recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
    return recommendations[:limit]

@app.get("/api/stats")
async def get_stats():
    """Get collection statistics"""
    games = load_games_data()
    if not games:
        raise HTTPException(status_code=404, detail="No games data found")
    
    # Calculate basic statistics
    total_games = len(games)
    games_with_ratings = len([g for g in games if g.get("rating") is not None])
    games_with_release_year = len([g for g in games if g.get("release_year") is not None])
    
    # Genre statistics
    all_genres = set()
    for game in games:
        all_genres.update(game.get("genres", []))
    
    # Theme statistics
    all_themes = set()
    for game in games:
        all_themes.update(game.get("themes", []))
    
    # Platform statistics
    all_platforms = set()
    for game in games:
        all_platforms.update(game.get("platforms", []))
    
    return {
        "total_games": total_games,
        "games_with_ratings": games_with_ratings,
        "games_with_release_year": games_with_release_year,
        "unique_genres": len(all_genres),
        "unique_themes": len(all_themes),
        "unique_platforms": len(all_platforms),
        "data_completeness": {
            "ratings": (games_with_ratings / total_games) * 100 if total_games > 0 else 0,
            "release_years": (games_with_release_year / total_games) * 100 if total_games > 0 else 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting IGDB Game Recommendation API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run("simple_api:app", host="0.0.0.0", port=8000, reload=True)
