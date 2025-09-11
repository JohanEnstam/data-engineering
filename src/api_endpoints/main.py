import json
import os

# Import our existing modules
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.append(str(Path(__file__).parent.parent))

from data_processing.data_validator import IGDBDataValidator
from models.game import BudgetInfo, DataQualityReport, Game

from .budget import router as budget_router
from .recommendations import router as recommendations_router

app = FastAPI(
    title="IGDB Game Recommendation API",
    description="API for IGDB game data and recommendations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(budget_router)
app.include_router(recommendations_router)

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def load_games_data() -> List[Game]:
    """Load games data from the processed JSON file"""
    try:
        # Find the most recent games file
        games_files = list(PROCESSED_DIR.glob("games_*.json"))
        if not games_files:
            raise FileNotFoundError("No games data files found")

        latest_file = max(games_files, key=lambda f: f.stat().st_mtime)

        with open(latest_file, "r", encoding="utf-8") as f:
            games_data = json.load(f)

        return games_data
    except Exception as e:
        print(f"Error loading games data: {e}")
        return []


def load_games_dataframe() -> pd.DataFrame:
    """Load games data as DataFrame for validation"""
    try:
        # Find the most recent games CSV file
        csv_files = list(PROCESSED_DIR.glob("games_*.csv"))
        if not csv_files:
            return None

        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)

        # Load as DataFrame
        df = pd.read_csv(latest_file)
        return df
    except Exception as e:
        print(f"Error loading games dataframe: {e}")
        return None


def load_data_quality_report() -> DataQualityReport:
    """Load data quality report by running validation on current data"""
    try:
        # Load the most recent games data
        games_df = load_games_dataframe()
        if games_df is None or games_df.empty:
            return DataQualityReport(
                total_games=0,
                validation_status="NO_DATA",
                issues=["No games data found"],
                statistics={},
                feature_statistics={
                    "genre_features": {"total_features": 0, "games_without_genres": 0},
                    "theme_features": {"total_features": 0, "games_without_themes": 0},
                    "platform_features": {
                        "total_features": 0,
                        "games_without_platforms": 0,
                    },
                },
            )

        # Run validation
        from data_processing.data_validator import IGDBDataValidator

        validator = IGDBDataValidator()
        validation_results = validator.validate_games_data(games_df)
        feature_results = validator.validate_feature_consistency(games_df)

        # Create report
        report = DataQualityReport(
            total_games=validation_results["total_games"],
            validation_status=(
                "PASSED" if validation_results["validation_passed"] else "FAILED"
            ),
            issues=validation_results["issues"],
            statistics=validation_results["statistics"],
            feature_statistics=feature_results,
        )

        return report
    except Exception as e:
        print(f"Error loading data quality report: {e}")
        return DataQualityReport(
            total_games=0,
            validation_status="ERROR",
            issues=[f"Error: {str(e)}"],
            statistics={},
            feature_statistics={
                "genre_features": {"total_features": 0, "games_without_genres": 0},
                "theme_features": {"total_features": 0, "games_without_themes": 0},
                "platform_features": {
                    "total_features": 0,
                    "games_without_platforms": 0,
                },
            },
        )


def load_budget_info() -> BudgetInfo:
    """Load budget information (mock data for now)"""
    return BudgetInfo(
        total_credits=300,
        used_credits=45,
        remaining_credits=255,
        monthly_estimate=85,
        services={"bigquery": 15, "cloud_run": 25, "vertex_ai": 0, "cloud_storage": 5},
    )


@app.get("/")
async def root():
    return {"message": "IGDB Game Recommendation API", "version": "1.0.0"}


@app.get("/api/games", response_model=List[Game])
async def get_games():
    """Get all games from the collection"""
    games = load_games_data()
    if not games:
        raise HTTPException(status_code=404, detail="No games data found")
    return games


@app.get("/api/games/{game_id}", response_model=Game)
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
        game
        for game in games
        if query_lower in game.get("name", "").lower()
        or query_lower in game.get("summary", "").lower()
    ]

    return filtered_games[:limit]


@app.get("/api/data-quality", response_model=DataQualityReport)
async def get_data_quality():
    """Get data quality report"""
    report = load_data_quality_report()
    if not report:
        raise HTTPException(status_code=404, detail="No data quality report found")
    return report


@app.get("/api/budget", response_model=BudgetInfo)
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

        genre_similarity = len(target_genres.intersection(game_genres)) / max(
            len(target_genres), 1
        )
        theme_similarity = len(target_themes.intersection(game_themes)) / max(
            len(target_themes), 1
        )

        # Weighted similarity score
        similarity_score = (genre_similarity * 0.7) + (theme_similarity * 0.3)

        if similarity_score > 0:
            recommendations.append(
                {
                    "game": game,
                    "similarity_score": similarity_score,
                    "reasons": [
                        f"Shares {len(target_genres.intersection(game_genres))} genres",
                        f"Shares {len(target_themes.intersection(game_themes))} themes",
                    ],
                }
            )

    # Sort by similarity score and return top recommendations
    recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
    return recommendations[:limit]


@app.get("/api/lookups")
async def get_lookups():
    """Get lookup tables for genres, themes, and platforms"""
    try:
        # Load raw lookup data
        raw_dir = DATA_DIR / "raw"

        # Load genres
        genres_files = list(raw_dir.glob("genres_*.json"))
        if genres_files:
            latest_genres = max(genres_files, key=lambda f: f.stat().st_mtime)
            with open(latest_genres, "r", encoding="utf-8") as f:
                genres_data = json.load(f)
            genres_lookup = {genre["id"]: genre["name"] for genre in genres_data}
        else:
            genres_lookup = {}

        # Load themes
        themes_files = list(raw_dir.glob("themes_*.json"))
        if themes_files:
            latest_themes = max(themes_files, key=lambda f: f.stat().st_mtime)
            with open(latest_themes, "r", encoding="utf-8") as f:
                themes_data = json.load(f)
            themes_lookup = {theme["id"]: theme["name"] for theme in themes_data}
        else:
            themes_lookup = {}

        # Load platforms
        platforms_files = list(raw_dir.glob("platforms_*.json"))
        if platforms_files:
            latest_platforms = max(platforms_files, key=lambda f: f.stat().st_mtime)
            with open(latest_platforms, "r", encoding="utf-8") as f:
                platforms_data = json.load(f)
            platforms_lookup = {
                platform["id"]: platform["name"] for platform in platforms_data
            }
        else:
            platforms_lookup = {}

        return {
            "genres": genres_lookup,
            "themes": themes_lookup,
            "platforms": platforms_lookup,
        }

    except Exception as e:
        print(f"Error loading lookup data: {e}")
        return {"genres": {}, "themes": {}, "platforms": {}}


@app.get("/api/stats")
async def get_stats():
    """Get collection statistics"""
    games = load_games_data()
    if not games:
        raise HTTPException(status_code=404, detail="No games data found")

    # Calculate basic statistics
    total_games = len(games)
    games_with_ratings = len([g for g in games if g.get("rating") is not None])
    games_with_release_year = len(
        [g for g in games if g.get("release_year") is not None]
    )

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
            "ratings": (
                (games_with_ratings / total_games) * 100 if total_games > 0 else 0
            ),
            "release_years": (
                (games_with_release_year / total_games) * 100 if total_games > 0 else 0
            ),
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
