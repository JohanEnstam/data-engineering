"""
IGDB Data Collector
Hämtar och sparar data från IGDB API för rekommendationssystemet
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from api.igdb_client import APIData

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IGDBDataCollector:
    """Hämtar och sparar IGDB data för ML-träning"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Skapa mappar om de inte finns
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Initiera IGDB client
        self.client = APIData()
        
    def collect_games(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """
        Hämtar speldata från IGDB API
        
        Args:
            limit: Antal spel att hämta per batch
            offset: Startposition för hämtning
            
        Returns:
            Lista med speldictionaries
        """
        logger.info(f"Hämtar {limit} spel från IGDB API (offset: {offset})")
        
        try:
            # Ladda environment variables
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            
            if not client_id or not client_secret:
                logger.error("CLIENT_ID eller CLIENT_SECRET saknas i .env")
                return []
            
            # Autentisera
            auth = self.client.authenticate(client_id, client_secret)
            if not auth or 'access_token' not in auth:
                logger.error("Autentisering misslyckades")
                return []
            
            # Hämta speldata
            fields = [
                "id", "name", "summary", "storyline", "rating", "rating_count",
                "release_dates", "genres", "themes", "platforms", "game_modes",
                "player_perspectives", "cover", "screenshots", "websites"
            ]
            
            self.client.api_fetch(
                url="https://api.igdb.com/v4/games",
                client_id=client_id,
                access_token=auth["access_token"],
                data_fields=fields,
                data_limit=limit
            )
            
            games = self.client.data
            logger.info(f"Hämtade {len(games)} spel")
            return games
            
        except Exception as e:
            logger.error(f"Fel vid hämtning av spel: {e}")
            return []
    
    def collect_genres(self) -> List[Dict]:
        """Hämtar alla genrer från IGDB API"""
        logger.info("Hämtar genrer från IGDB API")
        
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            
            if not client_id or not client_secret:
                logger.error("CLIENT_ID eller CLIENT_SECRET saknas i .env")
                return []
            
            # Autentisera
            auth = self.client.authenticate(client_id, client_secret)
            if not auth or 'access_token' not in auth:
                logger.error("Autentisering misslyckades")
                return []
            
            # Hämta genrer
            self.client.api_fetch(
                url="https://api.igdb.com/v4/genres",
                client_id=client_id,
                access_token=auth["access_token"],
                data_fields=["id", "name", "slug"],
                data_limit=100
            )
            
            genres = self.client.data
            logger.info(f"Hämtade {len(genres)} genrer")
            return genres
        except Exception as e:
            logger.error(f"Fel vid hämtning av genrer: {e}")
            return []
    
    def collect_platforms(self) -> List[Dict]:
        """Hämtar alla plattformar från IGDB API"""
        logger.info("Hämtar plattformar från IGDB API")
        
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            
            if not client_id or not client_secret:
                logger.error("CLIENT_ID eller CLIENT_SECRET saknas i .env")
                return []
            
            # Autentisera
            auth = self.client.authenticate(client_id, client_secret)
            if not auth or 'access_token' not in auth:
                logger.error("Autentisering misslyckades")
                return []
            
            # Hämta plattformar
            self.client.api_fetch(
                url="https://api.igdb.com/v4/platforms",
                client_id=client_id,
                access_token=auth["access_token"],
                data_fields=["id", "name", "slug", "category"],
                data_limit=100
            )
            
            platforms = self.client.data
            logger.info(f"Hämtade {len(platforms)} plattformar")
            return platforms
        except Exception as e:
            logger.error(f"Fel vid hämtning av plattformar: {e}")
            return []
    
    def collect_themes(self) -> List[Dict]:
        """Hämtar alla teman från IGDB API"""
        logger.info("Hämtar teman från IGDB API")
        
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            
            if not client_id or not client_secret:
                logger.error("CLIENT_ID eller CLIENT_SECRET saknas i .env")
                return []
            
            # Autentisera
            auth = self.client.authenticate(client_id, client_secret)
            if not auth or 'access_token' not in auth:
                logger.error("Autentisering misslyckades")
                return []
            
            # Hämta teman
            self.client.api_fetch(
                url="https://api.igdb.com/v4/themes",
                client_id=client_id,
                access_token=auth["access_token"],
                data_fields=["id", "name", "slug"],
                data_limit=100
            )
            
            themes = self.client.data
            logger.info(f"Hämtade {len(themes)} teman")
            return themes
        except Exception as e:
            logger.error(f"Fel vid hämtning av teman: {e}")
            return []
    
    def save_raw_data(self, data: List[Dict], data_type: str, timestamp: str = None) -> str:
        """
        Sparar rådata till JSON-fil
        
        Args:
            data: Data att spara
            data_type: Typ av data (games, genres, platforms, themes)
            timestamp: Tidsstämpel för filnamn
            
        Returns:
            Sökväg till sparad fil
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{data_type}_{timestamp}.json"
        filepath = self.raw_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Sparade {len(data)} {data_type} till {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Fel vid sparande av {data_type}: {e}")
            return ""
    
    def collect_all_data(self, games_limit: int = 1000) -> Dict[str, str]:
        """
        Hämtar all nödvändig data för rekommendationssystemet
        
        Args:
            games_limit: Antal spel att hämta
            
        Returns:
            Dictionary med sökvägar till sparade filer
        """
        logger.info("Börjar hämtning av all IGDB data")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_files = {}
        
        # Hämtar speldata
        games = self.collect_games(limit=games_limit)
        if games:
            saved_files['games'] = self.save_raw_data(games, 'games', timestamp)
        
        # Hämtar metadata
        genres = self.collect_genres()
        if genres:
            saved_files['genres'] = self.save_raw_data(genres, 'genres', timestamp)
        
        platforms = self.collect_platforms()
        if platforms:
            saved_files['platforms'] = self.save_raw_data(platforms, 'platforms', timestamp)
        
        themes = self.collect_themes()
        if themes:
            saved_files['themes'] = self.save_raw_data(themes, 'themes', timestamp)
        
        # Spara metadata om hämtningen
        collection_metadata = {
            "timestamp": timestamp,
            "games_count": len(games),
            "genres_count": len(genres),
            "platforms_count": len(platforms),
            "themes_count": len(themes),
            "files": saved_files
        }
        
        metadata_file = self.raw_dir / f"collection_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(collection_metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data collection klar. Metadata sparad till {metadata_file}")
        return saved_files

def main():
    """Huvudfunktion för data collection"""
    collector = IGDBDataCollector()
    
    # Testa med en mindre batch först
    print("Hämtar testdata från IGDB API...")
    saved_files = collector.collect_all_data(games_limit=100)
    
    print("\nSparade filer:")
    for data_type, filepath in saved_files.items():
        print(f"  {data_type}: {filepath}")

if __name__ == "__main__":
    main()
