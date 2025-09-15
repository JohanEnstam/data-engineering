"""
FastAPI backend for IGDB Game Recommendation API
BigQuery-integrated version for Cloud Run deployment
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .bigquery_client import BigQueryClient

app = FastAPI(
    title="IGDB Game Recommendation API",
    description="API for IGDB game data and recommendations (BigQuery version)",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Cloud Run
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize BigQuery client
bq_client = BigQueryClient()


class GameResponse(BaseModel):
    """Response model for game data"""
    id: int
    name: str
    summary: Optional[str] = None
    rating: Optional[float] = None
    release_year: Optional[str] = None
    genres: List[int] = []
    platforms: List[int] = []
    themes: List[int] = []
    game_modes: List[int] = []
    player_perspectives: List[int] = []
    collected_at: Optional[str] = None


class GamesResponse(BaseModel):
    """Response model for multiple games"""
    games: List[GameResponse]
    total_count: int
    message: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IGDB Game Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "bigquery_project": bq_client.project_id,
        "bigquery_dataset": bq_client.dataset_id
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        games_count = bq_client.get_games_count()
        return {
            "status": "healthy",
            "bigquery_connected": True,
            "games_count": games_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "bigquery_connected": False,
            "error": str(e)
        }


@app.get("/games", response_model=GamesResponse)
async def get_games(
    limit: int = Query(100, ge=1, le=1000, description="Number of games to retrieve"),
    search: str = Query(None, description="Search term for game names")
):
    """
    Get games data from BigQuery
    
    Args:
        limit: Maximum number of games to retrieve (1-1000)
        search: Optional search term for game names
    """
    try:
        if search:
            games_data = bq_client.search_games(search, limit)
        else:
            games_data = bq_client.get_games_data(limit)
        
        total_count = bq_client.get_games_count()
        
        # Convert to response model
        games = [GameResponse(**game) for game in games_data]
        
        return GamesResponse(
            games=games,
            total_count=total_count,
            message=f"Retrieved {len(games)} games from BigQuery"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving games: {str(e)}")


@app.get("/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: int):
    """
    Get a specific game by ID
    
    Args:
        game_id: The ID of the game to retrieve
    """
    try:
        # Search for specific game ID
        games_data = bq_client.search_games(str(game_id), 1)
        
        if not games_data:
            raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
        
        # Find exact match
        game = None
        for g in games_data:
            if g['id'] == game_id:
                game = g
                break
        
        if not game:
            raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")
        
        return GameResponse(**game)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving game: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        games_count = bq_client.get_games_count()
        
        return {
            "total_games": games_count,
            "bigquery_project": bq_client.project_id,
            "bigquery_dataset": bq_client.dataset_id,
            "status": "connected"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
