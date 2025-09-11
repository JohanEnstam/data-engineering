"""
Recommendations API Endpoints
FastAPI endpoints för spelrekommendationer
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from models.game_recommender import GameRecommender
except ImportError as e:
    logger.error(f"Failed to import GameRecommender: {e}")
    GameRecommender = None

# Create router
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Global recommender instance
recommender = None


def get_recommender():
    """Lazy load recommender model"""
    global recommender
    if recommender is None:
        if GameRecommender is None:
            raise HTTPException(status_code=500, detail="GameRecommender not available")

        recommender = GameRecommender()
        # Load the latest model
        models_dir = Path("data/models")
        model_files = list(models_dir.glob("game_recommender_*.pkl"))
        if model_files:
            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            recommender.load_model(latest_model.name)
            logger.info(f"Loaded model: {latest_model.name}")
        else:
            raise HTTPException(status_code=500, detail="No trained model found")
    return recommender


@router.get("/search")
async def search_games(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Number of results to return"),
) -> List[Dict]:
    """
    Search for games by name
    """
    try:
        recommender = get_recommender()
        results = recommender.search_games(q, limit)

        # Add cover URLs
        for result in results:
            cover_id = result.get("cover_id")
            if cover_id and not pd.isna(cover_id):
                result["cover_url"] = (
                    f"https://images.igdb.com/igdb/image/upload/t_cover_big/{int(cover_id)}.jpg"
                )
            else:
                result["cover_url"] = None

        return results

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{game_id}")
async def get_recommendations(
    game_id: int,
    limit: int = Query(3, description="Number of recommendations to return"),
) -> List[Dict]:
    """
    Get game recommendations for a specific game
    """
    try:
        recommender = get_recommender()
        recommendations = recommender.get_recommendations(game_id, limit)

        # Add cover URLs
        for rec in recommendations:
            cover_id = rec.get("cover_id")
            if cover_id and not pd.isna(cover_id):
                rec["cover_url"] = (
                    f"https://images.igdb.com/igdb/image/upload/t_cover_big/{int(cover_id)}.jpg"
                )
            else:
                rec["cover_url"] = None

        return recommendations

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/games/{game_id}")
async def get_game_details(game_id: int) -> Dict:
    """
    Get detailed information about a specific game
    """
    try:
        recommender = get_recommender()

        # Find game in dataframe
        game_row = recommender.games_df[recommender.games_df["id"] == game_id]
        if game_row.empty:
            raise HTTPException(status_code=404, detail="Game not found")

        game = game_row.iloc[0]

        return {
            "id": int(game["id"]),
            "name": game["name"],
            "summary": game.get("summary", ""),
            "rating": game.get("rating", 0),
            "genres": game.get("genres", ""),
            "themes": game.get("themes", ""),
            "platforms": game.get("platforms", ""),
            "cover_url": (
                f"https://images.igdb.com/igdb/image/upload/t_cover_big/{game.get('cover_id', '')}.jpg"
                if game.get("cover_id")
                else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Game details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Recommendations API is running"}
