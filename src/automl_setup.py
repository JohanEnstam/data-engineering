#!/usr/bin/env python3
"""
AutoML Setup Script för IGDB Game Recommendations
Konfigurerar Vertex AI AutoML för automatisk modellträning
"""

import os
import pandas as pd
from google.cloud import bigquery
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
import json
from datetime import datetime

# Konfiguration
PROJECT_ID = "exalted-tempo-471613-e2"
DATASET_ID = "igdb_game_data"
TABLE_ID = "games_raw"
REGION = "europe-west1"
BUCKET_NAME = "igdb-ml-pipeline-automl"

def setup_automl_dataset():
    """Skapa AutoML dataset från BigQuery data"""
    
    print("🚀 Konfigurerar AutoML för IGDB Game Recommendations...")
    
    # Initiera BigQuery client
    client = bigquery.Client(project=PROJECT_ID)
    
    # Ladda data från BigQuery
    print("📊 Laddar data från BigQuery...")
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
        player_perspectives
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    WHERE summary IS NOT NULL 
    AND rating IS NOT NULL
    AND name IS NOT NULL
    """
    
    df = client.query(query).to_dataframe()
    print(f"✅ Laddat {len(df)} spel från BigQuery")
    
    # Förbereda data för AutoML
    print("🔧 Förbereder data för AutoML...")
    
    # Skapa feature columns för AutoML
    automl_data = []
    
    for _, row in df.iterrows():
        # Konvertera arrays till strings för AutoML
        genres_str = ', '.join(map(str, row['genres'])) if row['genres'] else ''
        platforms_str = ', '.join(map(str, row['platforms'])) if row['platforms'] else ''
        themes_str = ', '.join(map(str, row['themes'])) if row['themes'] else ''
        game_modes_str = ', '.join(map(str, row['game_modes'])) if row['game_modes'] else ''
        player_perspectives_str = ', '.join(map(str, row['player_perspectives'])) if row['player_perspectives'] else ''
        
        automl_data.append({
            'game_id': int(row['id']),
            'name': str(row['name']),
            'summary': str(row['summary']),
            'rating': float(row['rating']),
            'release_year': int(row['release_year']) if row['release_year'] else 0,
            'genres': genres_str,
            'platforms': platforms_str,
            'themes': themes_str,
            'game_modes': game_modes_str,
            'player_perspectives': player_perspectives_str,
            'rating_category': 'High' if row['rating'] >= 75 else 'Medium' if row['rating'] >= 60 else 'Low'
        })
    
    # Skapa DataFrame
    automl_df = pd.DataFrame(automl_data)
    
    # Spara som CSV för AutoML
    csv_filename = f"automl_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    automl_df.to_csv(csv_filename, index=False)
    
    print(f"✅ Data förberedd och sparad som {csv_filename}")
    print(f"📊 Dataset innehåller {len(automl_df)} spel med {len(automl_df.columns)} features")
    
    # Visa data sample
    print("\n📋 Data Sample:")
    print(automl_df[['name', 'rating', 'rating_category', 'genres']].head())
    
    return csv_filename, automl_df

def create_automl_dataset(csv_filename):
    """Skapa AutoML dataset i Vertex AI"""
    
    print("\n🤖 Skapar AutoML dataset...")
    
    # Initiera Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # För nu, skapa dataset direkt från lokal fil
    # I production skulle vi ladda upp till GCS först
    dataset = aiplatform.TabularDataset.create(
        display_name=f"igdb-games-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        gcs_source=[f"gs://{BUCKET_NAME}/{csv_filename}"],
        labels={"project": "igdb-recommendations", "version": "v1"}
    )
    
    print(f"✅ AutoML dataset skapat: {dataset.resource_name}")
    return dataset

def setup_automl_training_job(dataset):
    """Konfigurera AutoML träningsjobb"""
    
    print("\n🎯 Konfigurerar AutoML träningsjobb...")
    
    # AutoML jobb konfiguration med korrekta parametrar
    job = aiplatform.AutoMLTabularTrainingJob(
        display_name=f"igdb-recommendations-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        optimization_objective="MINIMIZE_MAE",  # Mean Absolute Error för rating prediction
        column_specs={
            "rating": "target_column",
            "summary": "text_column",
            "genres": "categorical_column",
            "platforms": "categorical_column",
            "themes": "categorical_column",
            "game_modes": "categorical_column",
            "player_perspectives": "categorical_column",
            "release_year": "numeric_column"
        },
        optimization_objective_recall_value=0.95,
        optimization_objective_precision_value=0.95,
        disable_early_stopping=False,
        enable_web_access=False,
        labels={"project": "igdb-recommendations", "version": "v1"}
    )
    
    print("✅ AutoML träningsjobb konfigurerat")
    return job

def main():
    """Huvudfunktion för AutoML setup"""
    
    print("🎮 IGDB AutoML Setup för Game Recommendations")
    print("=" * 50)
    
    try:
        # Steg 1: Förbereda data
        csv_filename, automl_df = setup_automl_dataset()
        
        # Steg 2: Skapa AutoML dataset
        dataset = create_automl_dataset(csv_filename)
        
        # Steg 3: Konfigurera träningsjobb
        job = setup_automl_training_job(dataset)
        
        print("\n🎉 AutoML setup komplett!")
        print(f"📁 Dataset: {dataset.resource_name}")
        print(f"🎯 Träningsjobb: {job.resource_name}")
        print(f"📊 Data: {len(automl_df)} spel redo för träning")
        
        # Spara konfiguration
        config = {
            "dataset_id": dataset.resource_name,
            "job_id": job.resource_name,
            "csv_filename": csv_filename,
            "data_size": len(automl_df),
            "created_at": datetime.now().isoformat()
        }
        
        with open("automl_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Konfiguration sparad i automl_config.json")
        
    except Exception as e:
        print(f"❌ Fel vid AutoML setup: {str(e)}")
        raise

if __name__ == "__main__":
    main()
