"""
Cloud Function för IGDB Data Collection
Samlar spel data från IGDB API och sparar till BigQuery
"""

import json
import requests
import base64
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
import os

from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_release_year(release_dates):
    """
    Extrahera release year från release_dates array
    Baserat på vår lokala ETL pipeline logik
    """
    if not release_dates:
        return None
    
    # IGDB release_dates är en array av release date ID:n
    # Vi behöver hämta faktisk release date data från IGDB API
    # För nu, returnera None och hantera detta senare
    return None

@app.route('/', methods=['POST', 'GET'])
def collect_igdb_data():
    """
    Cloud Run service för att samla IGDB data
    Trigger: HTTP request eller Cloud Scheduler
    """
    
    # Konfiguration från environment variables
    PROJECT_ID = os.environ.get('PROJECT_ID', 'exalted-tempo-471613-e2')
    RAW_BUCKET = os.environ.get('RAW_BUCKET', 'igdb-raw-data-eu-1757661329')
    DATASET_ID = os.environ.get('DATASET_ID', 'igdb_game_data')
    
    # IGDB API credentials från Secret Manager
    CLIENT_ID = os.environ.get('IGDB_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('IGDB_CLIENT_SECRET')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        return {"error": "IGDB credentials not found"}, 400
    
    try:
        # Steg 1: Hämta access token från IGDB
        token_url = "https://id.twitch.tv/oauth2/token"
        token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
        
        # Steg 2: Samla spel data från IGDB
        games_data = []
        offset = 0
        limit = 500  # IGDB max per request
        
        # Hämta antal spel från request (default 100)
        games_limit = 100
        if request.method == 'POST':
            request_data = request.get_json() or {}
            games_limit = request_data.get('games_limit', 100)
        
        while len(games_data) < games_limit:
            # IGDB API query för att hämta spel
            # För nu, hoppar över release_dates eftersom vi inte hanterar dem korrekt
            query = f"""
            fields id,name,summary,rating,genres,platforms,themes,game_modes,player_perspectives;
            where rating != null & summary != null;
            sort rating desc;
            limit {limit};
            offset {offset};
            """
            
            headers = {
                "Client-ID": CLIENT_ID,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "text/plain"
            }
            
            response = requests.post(
                "https://api.igdb.com/v4/games",
                data=query,
                headers=headers
            )
            response.raise_for_status()
            
            batch_games = response.json()
            if not batch_games:
                break
                
            games_data.extend(batch_games)
            offset += limit
            
            print(f"Collected {len(games_data)} games so far...")
            
            # Stoppa om vi har tillräckligt
            if len(games_data) >= games_limit:
                games_data = games_data[:games_limit]
                break
        
        # Steg 3: Processa och rensa data
        processed_games = []
        for game in games_data:
            processed_game = {
                "id": game.get("id"),
                "name": game.get("name"),
                "summary": game.get("summary"),
                "rating": game.get("rating"),
                "release_year": None,  # Hanteras senare när vi implementerar release_dates korrekt
                "genres": game.get("genres", []),
                "platforms": game.get("platforms", []),
                "themes": game.get("themes", []),
                "game_modes": game.get("game_modes", []),
                "player_perspectives": game.get("player_perspectives", []),
                "collected_at": datetime.now().isoformat()
            }
            processed_games.append(processed_game)
        
        # Steg 4: Spara till Cloud Storage
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"raw_data/games_{timestamp}.json"
        
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(RAW_BUCKET)
        blob = bucket.blob(filename)
        
        # Spara som NDJSON (en JSON per rad)
        ndjson_data = "\n".join([json.dumps(game) for game in processed_games])
        blob.upload_from_string(ndjson_data, content_type='application/json')
        
        # Steg 5: Ladda till BigQuery
        table_id = f"{PROJECT_ID}.{DATASET_ID}.games_raw"
        source_uri = f"gs://{RAW_BUCKET}/{filename}"
        
        bq_client = bigquery.Client(project=PROJECT_ID)
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
            autodetect=True
        )
        
        load_job = bq_client.load_table_from_uri(
            source_uri, table_id, job_config=job_config
        )
        load_job.result()  # Vänta på att jobbet är klart
        
        return jsonify({
            "status": "success",
            "games_collected": len(processed_games),
            "file_saved": filename,
            "bigquery_table": table_id,
            "timestamp": timestamp
        })
        
    except Exception as e:
        print(f"Error in IGDB data collection: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
