export interface Game {
  id: number;
  name: string;
  summary: string;
  storyline: string | null;
  rating: number | null;
  rating_count: number;
  release_date: string | null;
  release_year: number | null;
  genres: number[];
  genre_count: number;
  themes: number[];
  theme_count: number;
  platforms: number[];
  platform_count: number;
  game_modes: number[];
  player_perspectives: number[];
  cover_id: number | null;
  cover_url: string | null;
  screenshot_ids: number[];
  screenshot_count: number;
  website_ids: number[];
  // ML features
  [key: string]: string | number | boolean | null | number[]; // For dynamic genre/theme features like genre_24, theme_1, etc.
}

export interface Genre {
  id: number;
  name: string;
  slug: string;
}

export interface Theme {
  id: number;
  name: string;
  slug: string;
}

export interface Platform {
  id: number;
  name: string;
  slug: string;
}

export interface GameRecommendation {
  game: Game;
  similarity_score: number;
  reasons: string[];
}

export interface DataQualityReport {
  total_games: number;
  validation_status: string;
  issues: string[];
  statistics: {
    rating: {
      min: number | null;
      max: number | null;
      mean: number | null;
      std: number | null;
    };
    release_year: {
      min: number | null;
      max: number | null;
      mean: number | null;
    };
    genres: {
      unique_genres: number;
      games_without_genres: number;
    };
    themes: {
      unique_themes: number;
      games_without_themes: number;
    };
    platforms: {
      unique_platforms: number;
      games_without_platforms: number;
    };
  };
  feature_statistics: {
    genre_features: {
      total_features: number;
      games_without_genres: number;
    };
    theme_features: {
      total_features: number;
      games_without_themes: number;
    };
    platform_features: {
      total_features: number;
      games_without_platforms: number;
    };
  };
}

export interface BudgetInfo {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  monthly_estimate: number;
  services: {
    bigquery: number;
    cloud_run: number;
    vertex_ai: number;
    cloud_storage: number;
  };
}
