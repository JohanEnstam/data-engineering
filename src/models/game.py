from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Game(BaseModel):
    id: int
    name: Optional[str] = None
    summary: Optional[str] = None
    storyline: Optional[str] = None
    rating: Optional[float] = None
    rating_count: int = 0
    release_date: Optional[Any] = None
    release_year: Optional[int] = None
    genres: List[int] = []
    genre_count: int = 0
    themes: List[int] = []
    theme_count: int = 0
    platforms: List[int] = []
    platform_count: int = 0
    game_modes: List[int] = []
    player_perspectives: List[int] = []
    cover_id: Optional[int] = None
    cover_url: Optional[str] = None
    screenshot_ids: List[int] = []
    screenshot_count: int = 0
    website_ids: List[int] = []


class Genre(BaseModel):
    id: int
    name: str
    slug: str


class Theme(BaseModel):
    id: int
    name: str
    slug: str


class Platform(BaseModel):
    id: int
    name: str
    slug: str


class GameRecommendation(BaseModel):
    game: Game
    similarity_score: float
    reasons: List[str]


class DataQualityReport(BaseModel):
    total_games: int
    validation_status: str
    issues: List[str]
    statistics: Dict[str, Any]
    feature_statistics: Dict[str, Any]


class BudgetInfo(BaseModel):
    total_credits: int
    used_credits: int
    remaining_credits: int
    monthly_estimate: int
    services: Dict[str, int]
