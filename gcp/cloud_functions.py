#!/usr/bin/env python3
"""
Cloud Functions för IGDB Data Collection
Migrerar vår lokala data collection till serverless Cloud Functions
"""

import os
import json
import requests
import base64
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
from google.cloud import functions_v1
from google.cloud.functions_v1.types import CloudFunction, EventTrigger, SourceRepository

# Konfiguration
PROJECT_ID = "exalted-tempo-471613-e2"
REGION = "europe-west1"
FUNCTION_NAME = "igdb-data-collector"
RAW_BUCKET = "igdb-raw-data-eu-1757661329"
DATASET_ID = "igdb_game_data"

def create_igdb_collector_function():
    """Skapa Cloud Function för IGDB data collection"""
    
    print("🚀 Skapar IGDB Data Collector Cloud Function...")
    
    # Function source code
    function_code = '''
import json
import requests
import base64
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery

def collect_igdb_data(request):
    """
    Cloud Function för att samla IGDB data
    Trigger: HTTP request eller Cloud Scheduler
    """
    
    # Konfiguration från environment variables
    PROJECT_ID = "exalted-tempo-471613-e2"
    RAW_BUCKET = "igdb-raw-data-eu-1757661329"
    DATASET_ID = "igdb_game_data"
    
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
        
        while len(games_data) < 1000:  # Samla 1000 spel
            # IGDB API query för att hämta spel
            query = f"""
            fields id,name,summary,rating,release_dates,genres,platforms,themes,game_modes,player_perspectives;
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
        
        # Steg 3: Processa och rensa data
        processed_games = []
        for game in games_data:
            processed_game = {
                "id": game.get("id"),
                "name": game.get("name"),
                "summary": game.get("summary"),
                "rating": game.get("rating"),
                "release_year": extract_release_year(game.get("release_dates", [])),
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
        ndjson_data = "\\n".join([json.dumps(game) for game in processed_games])
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
        
        return {
            "status": "success",
            "games_collected": len(processed_games),
            "file_saved": filename,
            "bigquery_table": table_id,
            "timestamp": timestamp
        }
        
    except Exception as e:
        print(f"Error in IGDB data collection: {str(e)}")
        return {"error": str(e)}, 500

def extract_release_year(release_dates):
    """Extrahera release year från release_dates array"""
    if not release_dates:
        return None
    
    # Ta första release date
    first_release = release_dates[0]
    if isinstance(first_release, dict) and "date" in first_release:
        release_date = first_release["date"]
        if release_date:
            return int(str(release_date)[:4])  # Ta första 4 siffror (år)
    
    return None
'''
    
    # Skapa Cloud Function
    client = functions_v1.CloudFunctionsServiceClient()
    
    function = CloudFunction(
        name=f"projects/{PROJECT_ID}/locations/{REGION}/functions/{FUNCTION_NAME}",
        description="IGDB Data Collection Function",
        entry_point="collect_igdb_data",
        runtime="python39",
        source_archive_url=f"gs://{RAW_BUCKET}/functions/{FUNCTION_NAME}.zip",
        https_trigger=CloudFunction.HttpsTrigger(),
        environment_variables={
            "PROJECT_ID": PROJECT_ID,
            "RAW_BUCKET": RAW_BUCKET,
            "DATASET_ID": DATASET_ID,
        },
        timeout="540s",  # 9 minuter timeout
        available_memory_mb=1024,  # 1GB RAM
        labels={
            "project": "igdb-recommendations",
            "function": "data-collection"
        }
    )
    
    print(f"✅ Cloud Function konfigurerad: {FUNCTION_NAME}")
    print(f"📍 Region: {REGION}")
    print(f"⏱️ Timeout: 9 minuter")
    print(f"💾 Memory: 1GB")
    
    return function

def setup_function_permissions():
    """Sätt upp permissions för Cloud Function"""
    
    print("\n🔐 Konfigurerar Function permissions...")
    
    # Service account för Cloud Function
    function_sa = f"{FUNCTION_NAME}@{PROJECT_ID}.iam.gserviceaccount.com"
    
    # Nödvändiga roller
    roles = [
        "roles/storage.objectAdmin",
        "roles/bigquery.dataEditor",
        "roles/secretmanager.secretAccessor"
    ]
    
    print(f"📋 Service Account: {function_sa}")
    print("📋 Nödvändiga roller:")
    for role in roles:
        print(f"  - {role}")
    
    print("\n💡 Kör följande kommandon:")
    for role in roles:
        print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} \\")
        print(f"    --member='serviceAccount:{function_sa}' \\")
        print(f"    --role='{role}'")
    
    return function_sa, roles

def create_scheduler_trigger():
    """Skapa Cloud Scheduler för automatisk data collection"""
    
    print("\n⏰ Konfigurerar Cloud Scheduler...")
    
    scheduler_config = {
        "name": "igdb-data-collection-schedule",
        "description": "Daily IGDB data collection",
        "schedule": "0 2 * * *",  # Varje dag kl 02:00 UTC
        "time_zone": "Europe/Stockholm",
        "target": {
            "http_target": {
                "uri": f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}",
                "http_method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "trigger": "scheduled",
                    "games_limit": 1000
                }).encode()
            }
        }
    }
    
    print("📋 Scheduler konfiguration:")
    print(f"  - Name: {scheduler_config['name']}")
    print(f"  - Schedule: {scheduler_config['schedule']} (Daily at 02:00)")
    print(f"  - Timezone: {scheduler_config['time_zone']}")
    print(f"  - Target: {scheduler_config['target']['http_target']['uri']}")
    
    return scheduler_config

def setup_secret_manager():
    """Sätt upp Secret Manager för IGDB credentials"""
    
    print("\n🔒 Konfigurerar Secret Manager...")
    
    secrets = [
        {
            "name": "igdb-client-id",
            "description": "IGDB/Twitch Client ID för API access"
        },
        {
            "name": "igdb-client-secret", 
            "description": "IGDB/Twitch Client Secret för API access"
        }
    ]
    
    print("📋 Secrets att skapa:")
    for secret in secrets:
        print(f"  - {secret['name']}: {secret['description']}")
    
    print("\n💡 Kör följande kommandon:")
    for secret in secrets:
        print(f"gcloud secrets create {secret['name']} \\")
        print(f"    --data-file=- \\")
        print(f"    --replication-policy='automatic'")
        print(f"echo 'your-secret-value' | gcloud secrets versions add {secret['name']} --data-file=-")
    
    return secrets

def main():
    """Huvudfunktion för Cloud Functions setup"""
    
    print("🎮 IGDB Cloud Functions Setup")
    print("=" * 50)
    
    try:
        # Steg 1: Skapa Cloud Function
        print("\n🚀 STEG 1: Skapar Cloud Function")
        function = create_igdb_collector_function()
        
        # Steg 2: Sätt upp permissions
        print("\n🔐 STEG 2: Konfigurerar Permissions")
        function_sa, roles = setup_function_permissions()
        
        # Steg 3: Skapa Scheduler trigger
        print("\n⏰ STEG 3: Konfigurerar Scheduler")
        scheduler_config = create_scheduler_trigger()
        
        # Steg 4: Sätt upp Secret Manager
        print("\n🔒 STEG 4: Konfigurerar Secret Manager")
        secrets = setup_secret_manager()
        
        # Spara konfiguration
        config = {
            "project_id": PROJECT_ID,
            "region": REGION,
            "function_name": FUNCTION_NAME,
            "function_sa": function_sa,
            "required_roles": roles,
            "scheduler_config": scheduler_config,
            "secrets": secrets,
            "raw_bucket": RAW_BUCKET,
            "dataset_id": DATASET_ID,
            "created_at": datetime.now().isoformat(),
            "status": "setup_configured"
        }
        
        with open("cloud_functions_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("\n🎉 Cloud Functions setup konfigurerad!")
        print(f"📁 Konfiguration sparad i cloud_functions_config.json")
        
        print("\n📋 NÄSTA STEG:")
        print("1. Skapa secrets i Secret Manager")
        print("2. Kör permission setup kommandon")
        print("3. Deploya Cloud Function")
        print("4. Skapa Cloud Scheduler job")
        print("5. Testa function via HTTP trigger")
        
        return config
        
    except Exception as e:
        print(f"❌ Fel vid Cloud Functions setup: {str(e)}")
        raise

if __name__ == "__main__":
    main()
