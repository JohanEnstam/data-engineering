"""
ETL Pipeline för IGDB Data
Transformarar rådata till ML-kompatibelt format
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IGDBETLPipeline:
    """ETL pipeline för IGDB data transformation"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Skapa processed mapp om den inte finns
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw_data(self, data_type: str, timestamp: str = None) -> List[Dict]:
        """
        Laddar rådata från JSON-fil
        
        Args:
            data_type: Typ av data (games, genres, platforms, themes)
            timestamp: Tidsstämpel för filnamn
            
        Returns:
            Lista med data dictionaries
        """
        if timestamp is None:
            # Hitta senaste filen av denna typ
            pattern = f"{data_type}_*.json"
            files = list(self.raw_dir.glob(pattern))
            if not files:
                logger.error(f"Ingen {data_type} data hittades")
                return []
            filepath = max(files, key=lambda x: x.stat().st_mtime)
        else:
            filepath = self.raw_dir / f"{data_type}_{timestamp}.json"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Laddade {len(data)} {data_type} från {filepath}")
            return data
        except Exception as e:
            logger.error(f"Fel vid laddning av {data_type}: {e}")
            return []
    
    def process_games(self, games: List[Dict]) -> pd.DataFrame:
        """
        Processar speldata till ML-kompatibelt format
        
        Args:
            games: Lista med speldictionaries
            
        Returns:
            DataFrame med processad speldata
        """
        logger.info(f"Processar {len(games)} spel")
        
        processed_games = []
        
        for game in games:
            try:
                # Extrahera grundläggande information
                processed_game = {
                    'id': game.get('id'),
                    'name': game.get('name', ''),
                    'summary': game.get('summary', ''),
                    'storyline': game.get('storyline', ''),
                    'rating': game.get('rating'),
                    'rating_count': game.get('rating_count', 0),
                }
                
                # Processa release dates (IGDB returnerar ID:n, inte objekt)
                release_dates = game.get('release_dates', [])
                if release_dates:
                    # IGDB returnerar release date ID:n, inte datum
                    processed_game['release_date'] = release_dates[0] if isinstance(release_dates[0], int) else None
                    processed_game['release_year'] = None  # Kommer att fyllas i senare
                else:
                    processed_game['release_date'] = None
                    processed_game['release_year'] = None
                
                # Processa genrer (IGDB returnerar ID:n, inte objekt)
                genres = game.get('genres', [])
                processed_game['genres'] = genres  # Behåll ID:n för nu
                processed_game['genre_count'] = len(processed_game['genres'])
                
                # Processa teman (IGDB returnerar ID:n, inte objekt)
                themes = game.get('themes', [])
                processed_game['themes'] = themes  # Behåll ID:n för nu
                processed_game['theme_count'] = len(processed_game['themes'])
                
                # Processa plattformar (IGDB returnerar ID:n, inte objekt)
                platforms = game.get('platforms', [])
                processed_game['platforms'] = platforms  # Behåll ID:n för nu
                processed_game['platform_count'] = len(processed_game['platforms'])
                
                # Processa game modes (IGDB returnerar ID:n, inte objekt)
                game_modes = game.get('game_modes', [])
                processed_game['game_modes'] = game_modes  # Behåll ID:n för nu
                
                # Processa player perspectives (IGDB returnerar ID:n, inte objekt)
                perspectives = game.get('player_perspectives', [])
                processed_game['player_perspectives'] = perspectives  # Behåll ID:n för nu
                
                # Processa cover (IGDB returnerar ID, inte objekt)
                cover = game.get('cover')
                processed_game['cover_id'] = cover if cover else None
                processed_game['cover_url'] = ''  # Kommer att fyllas i senare
                
                # Processa screenshots (IGDB returnerar ID:n, inte objekt)
                screenshots = game.get('screenshots', [])
                processed_game['screenshot_ids'] = screenshots
                processed_game['screenshot_count'] = len(processed_game['screenshot_ids'])
                
                # Processa websites (IGDB returnerar ID:n, inte objekt)
                websites = game.get('websites', [])
                processed_game['website_ids'] = websites
                
                processed_games.append(processed_game)
                
            except Exception as e:
                logger.warning(f"Fel vid processning av spel {game.get('id', 'unknown')}: {e}")
                continue
        
        # Skapa DataFrame
        df = pd.DataFrame(processed_games)
        
        # Konvertera numeriska kolumner
        numeric_columns = ['rating', 'rating_count', 'genre_count', 'theme_count', 'platform_count', 'screenshot_count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Konvertera release_year till int
        if 'release_year' in df.columns:
            df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
        
        logger.info(f"Processade {len(df)} spel till DataFrame")
        return df
    
    def create_genre_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Skapar one-hot encoded features för genrer
        
        Args:
            df: DataFrame med speldata
            
        Returns:
            DataFrame med genre features
        """
        logger.info("Skapar genre features")
        
        # Samla alla unika genre ID:n
        all_genres = set()
        for genres in df['genres']:
            if isinstance(genres, list):
                all_genres.update(genres)
        
        # Skapa one-hot encoded kolumner
        for genre_id in all_genres:
            if genre_id:  # Skip empty values
                df[f'genre_{genre_id}'] = df['genres'].apply(
                    lambda x: 1 if isinstance(x, list) and genre_id in x else 0
                )
        
        logger.info(f"Skapade {len(all_genres)} genre features")
        return df
    
    def create_theme_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Skapar one-hot encoded features för teman
        
        Args:
            df: DataFrame med speldata
            
        Returns:
            DataFrame med theme features
        """
        logger.info("Skapar theme features")
        
        # Samla alla unika theme ID:n
        all_themes = set()
        for themes in df['themes']:
            if isinstance(themes, list):
                all_themes.update(themes)
        
        # Skapa one-hot encoded kolumner
        for theme_id in all_themes:
            if theme_id:  # Skip empty values
                df[f'theme_{theme_id}'] = df['themes'].apply(
                    lambda x: 1 if isinstance(x, list) and theme_id in x else 0
                )
        
        logger.info(f"Skapade {len(all_themes)} theme features")
        return df
    
    def create_platform_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Skapar one-hot encoded features för plattformar
        
        Args:
            df: DataFrame med speldata
            
        Returns:
            DataFrame med platform features
        """
        logger.info("Skapar platform features")
        
        # Samla alla unika platform ID:n
        all_platforms = set()
        for platforms in df['platforms']:
            if isinstance(platforms, list):
                all_platforms.update(platforms)
        
        # Skapa one-hot encoded kolumner
        for platform_id in all_platforms:
            if platform_id:  # Skip empty values
                df[f'platform_{platform_id}'] = df['platforms'].apply(
                    lambda x: 1 if isinstance(x, list) and platform_id in x else 0
                )
        
        logger.info(f"Skapade {len(all_platforms)} platform features")
        return df
    
    def save_processed_data(self, df: pd.DataFrame, data_type: str, timestamp: str = None) -> str:
        """
        Sparar processad data till CSV och JSON
        
        Args:
            df: DataFrame med processad data
            data_type: Typ av data
            timestamp: Tidsstämpel för filnamn
            
        Returns:
            Sökväg till sparad fil
        """
        if timestamp is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Spara som CSV
        csv_file = self.processed_dir / f"{data_type}_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        
        # Spara som JSON
        json_file = self.processed_dir / f"{data_type}_{timestamp}.json"
        df.to_json(json_file, orient='records', indent=2)
        
        logger.info(f"Sparade processad {data_type} data till {csv_file} och {json_file}")
        return str(csv_file)
    
    def run_full_etl(self, timestamp: str = None) -> Dict[str, str]:
        """
        Kör fullständig ETL pipeline
        
        Args:
            timestamp: Tidsstämpel för data att processa
            
        Returns:
            Dictionary med sökvägar till processade filer
        """
        logger.info("Börjar ETL pipeline")
        
        # Ladda rådata
        games = self.load_raw_data('games', timestamp)
        if not games:
            logger.error("Ingen speldata att processa")
            return {}
        
        # Processa speldata
        df = self.process_games(games)
        
        # Skapa features
        df = self.create_genre_features(df)
        df = self.create_theme_features(df)
        df = self.create_platform_features(df)
        
        # Spara processad data
        processed_file = self.save_processed_data(df, 'games', timestamp)
        
        # Spara metadata
        metadata = {
            "timestamp": timestamp or pd.Timestamp.now().strftime("%Y%m%d_%H%M%S"),
            "total_games": len(df),
            "features": list(df.columns),
            "processed_file": processed_file
        }
        
        metadata_file = self.processed_dir / f"etl_metadata_{metadata['timestamp']}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"ETL pipeline klar. Metadata sparad till {metadata_file}")
        return {"processed_file": processed_file, "metadata": str(metadata_file)}

def main():
    """Huvudfunktion för ETL pipeline"""
    pipeline = IGDBETLPipeline()
    
    print("Kör ETL pipeline...")
    result = pipeline.run_full_etl()
    
    print("\nProcessade filer:")
    for key, filepath in result.items():
        print(f"  {key}: {filepath}")

if __name__ == "__main__":
    main()
