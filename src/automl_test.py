#!/usr/bin/env python3
"""
AutoML Test Script för IGDB Game Recommendations
Testar AutoML funktionalitet med vår BigQuery data
"""

import os
import pandas as pd
from google.cloud import bigquery
from google.cloud import aiplatform
import json
from datetime import datetime

# Konfiguration
PROJECT_ID = "exalted-tempo-471613-e2"
DATASET_ID = "igdb_game_data"
TABLE_ID = "games_raw"
REGION = "europe-west1"

def test_automl_data_preparation():
    """Testa data förberedelse för AutoML"""
    
    print("🚀 Testar AutoML data förberedelse...")
    
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
    
    # Visa data statistik
    print("\n📈 Data Statistik:")
    print(f"Rating range: {automl_df['rating'].min():.2f} - {automl_df['rating'].max():.2f}")
    print(f"Release year range: {automl_df['release_year'].min()} - {automl_df['release_year'].max()}")
    print(f"Rating categories: {automl_df['rating_category'].value_counts().to_dict()}")
    
    return csv_filename, automl_df

def test_vertex_ai_connection():
    """Testa Vertex AI anslutning"""
    
    print("\n🤖 Testar Vertex AI anslutning...")
    
    try:
        # Initiera Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        print("✅ Vertex AI initierad framgångsrikt")
        
        # Testa att lista datasets
        datasets = aiplatform.TabularDataset.list()
        print(f"📊 Hittade {len(datasets)} befintliga datasets")
        
        return True
        
    except Exception as e:
        print(f"❌ Fel vid Vertex AI anslutning: {str(e)}")
        return False

def test_automl_capabilities():
    """Testa AutoML funktionalitet"""
    
    print("\n🎯 Testar AutoML funktionalitet...")
    
    try:
        # Testa AutoML jobb konfiguration med korrekta parametrar
        job = aiplatform.AutoMLTabularTrainingJob(
            display_name=f"test-igdb-recommendations-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            optimization_prediction_type="regression",  # För rating prediction
            optimization_objective="minimize-mae",  # Mean Absolute Error
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
            labels={"project": "igdb-recommendations", "version": "test"}
        )
        
        print("✅ AutoML jobb konfiguration fungerar")
        return job
        
    except Exception as e:
        print(f"❌ Fel vid AutoML konfiguration: {str(e)}")
        return None

def main():
    """Huvudfunktion för AutoML test"""
    
    print("🎮 IGDB AutoML Test för Game Recommendations")
    print("=" * 50)
    
    try:
        # Steg 1: Testa data förberedelse
        csv_filename, automl_df = test_automl_data_preparation()
        
        # Steg 2: Testa Vertex AI anslutning
        vertex_ai_ok = test_vertex_ai_connection()
        
        if vertex_ai_ok:
            # Steg 3: Testa AutoML funktionalitet
            job = test_automl_capabilities()
            
            if job:
                print("\n🎉 AutoML test komplett!")
                print(f"📁 Data: {csv_filename}")
                print(f"📊 Dataset: {len(automl_df)} spel redo för träning")
                print(f"🎯 AutoML jobb: Konfigurerat (inte skapat ännu)")
                
                # Spara test resultat
                test_results = {
                    "csv_filename": csv_filename,
                    "data_size": len(automl_df),
                    "vertex_ai_connection": vertex_ai_ok,
                    "automl_job_configured": job is not None,
                    "job_display_name": "test-igdb-recommendations" if job else None,
                    "tested_at": datetime.now().isoformat()
                }
                
                with open("automl_test_results.json", "w") as f:
                    json.dump(test_results, f, indent=2)
                
                print(f"💾 Test resultat sparade i automl_test_results.json")
            else:
                print("❌ AutoML konfiguration misslyckades")
        else:
            print("❌ Vertex AI anslutning misslyckades")
        
    except Exception as e:
        print(f"❌ Fel vid AutoML test: {str(e)}")
        raise

if __name__ == "__main__":
    main()
