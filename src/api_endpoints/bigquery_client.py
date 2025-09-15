"""
BigQuery client for FastAPI backend
Handles data retrieval from BigQuery instead of local files
"""

import os
from typing import List, Dict, Any
from google.cloud import bigquery
import pandas as pd


class BigQueryClient:
    """Client for interacting with BigQuery"""
    
    def __init__(self):
        self.project_id = os.environ.get('PROJECT_ID', 'exalted-tempo-471613-e2')
        self.dataset_id = os.environ.get('DATASET_ID', 'igdb_game_data')
        self.client = bigquery.Client(project=self.project_id)
    
    def get_games_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve games data from BigQuery
        
        Args:
            limit: Maximum number of games to retrieve
            
        Returns:
            List of game dictionaries
        """
        query = f"""
        SELECT 
            id,
            name,
            summary,
            rating,
            release_year,
            genres,
            platforms,
            themes,
            game_modes,
            player_perspectives,
            collected_at
        FROM `{self.project_id}.{self.dataset_id}.games_raw`
        ORDER BY collected_at DESC
        LIMIT {limit}
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            games_data = []
            for row in results:
                # Hantera release_year korrekt - det kan vara NULL eller string
                release_year = None
                if row.release_year:
                    # Om det är en string, använd den direkt
                    if isinstance(row.release_year, str):
                        release_year = row.release_year
                    # Om det är en integer, konvertera till string
                    elif isinstance(row.release_year, int):
                        release_year = str(row.release_year)
                
                game_dict = {
                    'id': row.id,
                    'name': row.name,
                    'summary': row.summary,
                    'rating': row.rating,
                    'release_year': release_year,  # Nu hanterat korrekt
                    'genres': row.genres if row.genres else [],
                    'platforms': row.platforms if row.platforms else [],
                    'themes': row.themes if row.themes else [],
                    'game_modes': row.game_modes if row.game_modes else [],
                    'player_perspectives': row.player_perspectives if row.player_perspectives else [],
                    'collected_at': row.collected_at.isoformat() if row.collected_at else None
                }
                games_data.append(game_dict)
            
            return games_data
            
        except Exception as e:
            print(f"Error querying BigQuery: {e}")
            return []
    
    def get_games_count(self) -> int:
        """Get total number of games in BigQuery"""
        query = f"""
        SELECT COUNT(*) as total_games
        FROM `{self.project_id}.{self.dataset_id}.games_raw`
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            row = next(results)
            return row.total_games
        except Exception as e:
            print(f"Error getting games count: {e}")
            return 0
    
    def search_games(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for games by name
        
        Args:
            search_term: Term to search for in game names
            limit: Maximum number of results
            
        Returns:
            List of matching games
        """
        query = f"""
        SELECT 
            id,
            name,
            summary,
            rating,
            release_year,
            genres,
            platforms,
            themes,
            game_modes,
            player_perspectives,
            collected_at
        FROM `{self.project_id}.{self.dataset_id}.games_raw`
        WHERE LOWER(name) LIKE LOWER('%{search_term}%')
        ORDER BY rating DESC
        LIMIT {limit}
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            games_data = []
            for row in results:
                # Hantera release_year korrekt - det kan vara NULL eller string
                release_year = None
                if row.release_year:
                    # Om det är en string, använd den direkt
                    if isinstance(row.release_year, str):
                        release_year = row.release_year
                    # Om det är en integer, konvertera till string
                    elif isinstance(row.release_year, int):
                        release_year = str(row.release_year)
                
                game_dict = {
                    'id': row.id,
                    'name': row.name,
                    'summary': row.summary,
                    'rating': row.rating,
                    'release_year': release_year,  # Nu hanterat korrekt
                    'genres': row.genres if row.genres else [],
                    'platforms': row.platforms if row.platforms else [],
                    'themes': row.themes if row.themes else [],
                    'game_modes': row.game_modes if row.game_modes else [],
                    'player_perspectives': row.player_perspectives if row.player_perspectives else [],
                    'collected_at': row.collected_at.isoformat() if row.collected_at else None
                }
                games_data.append(game_dict)
            
            return games_data
            
        except Exception as e:
            print(f"Error searching games: {e}")
            return []
