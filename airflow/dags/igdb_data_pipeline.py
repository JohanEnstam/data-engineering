"""
IGDB Data Pipeline DAG
=====================

This DAG orchestrates the complete data pipeline from IGDB API to ML models:
1. Collect data from IGDB API
2. Upload raw data to Cloud Storage
3. Load data to BigQuery
4. Run dbt transformations
5. Train ML models

Author: Data Engineering Team
Date: 2025-01-11
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import os
import json
import logging

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'igdb_data_pipeline',
    default_args=default_args,
    description='Complete IGDB data pipeline from API to ML models',
    schedule=timedelta(days=1),  # Run daily
    catchup=False,
    tags=['igdb', 'data-pipeline', 'ml'],
)

# Configuration
PROJECT_ID = 'exalted-tempo-471613-e2'
DATASET_ID = 'igdb_games'
RAW_BUCKET = 'igdb-raw-data-1757587379'
PROCESSED_BUCKET = 'igdb-processed-data-1757587387'
SERVICE_ACCOUNT_KEY = '/Users/johanenstam/Sync/Utveckling/data-engineering/frontend/src/github-actions-key.json'

def collect_igdb_data(**context):
    """
    Collect data from IGDB API and save to local file
    """
    import sys
    sys.path.append('/Users/johanenstam/Sync/Utveckling/data-engineering')
    
    from src.data_collectors.igdb_data_collector import IGDBDataCollector
    
    # Set up logging
    logging.info("Starting IGDB data collection...")
    
    # Collect data using existing collector
    try:
        collector = IGDBDataCollector()
        games_data = collector.collect_games(limit=100)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"games_{timestamp}.json"
        filepath = f"/Users/johanenstam/Sync/Utveckling/data-engineering/data/raw/{filename}"
        
        import json
        with open(filepath, 'w') as f:
            json.dump(games_data, f, indent=2)
        
        logging.info(f"Collected {len(games_data)} games and saved to: {filename}")
        
        # Return file path for next task
        return {
            'local_file_path': filepath,
            'file_name': filename
        }
        
    except Exception as e:
        logging.error(f"Error collecting IGDB data: {str(e)}")
        raise

def upload_to_gcs(**context):
    """
    Upload collected data to Google Cloud Storage
    """
    from airflow.providers.google.cloud.hooks.gcs import GCSHook
    
    # Get file info from previous task
    ti = context['ti']
    file_info = ti.xcom_pull(task_ids='collect_igdb_data')
    local_file_path = file_info['local_file_path']
    file_name = file_info['file_name']
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    gcs_filename = f"raw_data/games_{timestamp}.json"
    
    # Upload to GCS
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    gcs_hook.upload(
        bucket_name=RAW_BUCKET,
        object_name=gcs_filename,
        filename=local_file_path,
        mime_type='application/json'
    )
    
    logging.info(f"Uploaded {file_name} to gs://{RAW_BUCKET}/{gcs_filename}")
    
    return {
        'gcs_bucket': RAW_BUCKET,
        'gcs_filename': gcs_filename
    }

def load_to_bigquery(**context):
    """
    Load data from GCS to BigQuery
    """
    from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
    
    # Get GCS file info from previous task
    ti = context['ti']
    gcs_info = ti.xcom_pull(task_ids='upload_to_gcs')
    gcs_filename = gcs_info['gcs_filename']
    
    # BigQuery configuration
    table_id = f"{PROJECT_ID}.{DATASET_ID}.games_raw"
    source_uri = f"gs://{RAW_BUCKET}/{gcs_filename}"
    
    # Load data to BigQuery
    bq_hook = BigQueryHook(gcp_conn_id='google_cloud_default')
    
    job_config = {
        'sourceFormat': 'NEWLINE_DELIMITED_JSON',
        'writeDisposition': 'WRITE_TRUNCATE',  # Replace existing data
        'createDisposition': 'CREATE_IF_NEEDED',
        'autodetect': True
    }
    
    job = bq_hook.insert_job(
        configuration={
            'load': {
                'destinationTable': {
                    'projectId': PROJECT_ID,
                    'datasetId': DATASET_ID,
                    'tableId': 'games_raw'
                },
                'sourceUris': [source_uri],
                'sourceFormat': 'NEWLINE_DELIMITED_JSON',
                'writeDisposition': 'WRITE_TRUNCATE',
                'createDisposition': 'CREATE_IF_NEEDED',
                'autodetect': True
            }
        }
    )
    
    logging.info(f"Loading data from {source_uri} to {table_id}")
    logging.info(f"Job ID: {job.job_id}")
    
    return {
        'table_id': table_id,
        'job_id': job.job_id
    }

def run_dbt_transformations(**context):
    """
    Run dbt transformations on the loaded data
    """
    dbt_project_dir = '/Users/johanenstam/Sync/Utveckling/data-engineering/dbt_igdb_project/igdb_models'
    
    # Set environment variables for dbt
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_KEY
    
    # Run dbt commands
    commands = [
        f"cd {dbt_project_dir} && dbt deps",
        f"cd {dbt_project_dir} && dbt run --profiles-dir ~/.dbt",
        f"cd {dbt_project_dir} && dbt test --profiles-dir ~/.dbt"
    ]
    
    for cmd in commands:
        logging.info(f"Running: {cmd}")
        os.system(cmd)
    
    logging.info("dbt transformations completed successfully")
    
    return {
        'dbt_status': 'completed',
        'models_run': ['stg_games', 'game_recommendations']
    }

def train_ml_models(**context):
    """
    Train ML models using the transformed data
    """
    import sys
    sys.path.append('/Users/johanenstam/Sync/Utveckling/data-engineering')
    
    from src.models.game_recommender import GameRecommender
    
    # Set up logging
    logging.info("Starting ML model training...")
    
    try:
        # Initialize and train the recommender
        recommender = GameRecommender()
        
        # Load data from BigQuery
        recommender.load_data_from_bigquery(
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID,
            table_id='game_recommendations'
        )
        
        # Train the model
        recommender.train()
        
        # Save the model
        model_path = f"/Users/johanenstam/Sync/Utveckling/data-engineering/data/models/game_recommender_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        recommender.save_model(model_path)
        
        logging.info(f"ML model trained and saved to: {model_path}")
        
        return {
            'model_path': model_path,
            'training_status': 'completed'
        }
        
    except Exception as e:
        logging.error(f"Error training ML model: {str(e)}")
        raise

# Task definitions
collect_data_task = PythonOperator(
    task_id='collect_igdb_data',
    python_callable=collect_igdb_data,
    dag=dag,
)

upload_to_gcs_task = PythonOperator(
    task_id='upload_to_gcs',
    python_callable=upload_to_gcs,
    dag=dag,
)

load_to_bigquery_task = PythonOperator(
    task_id='load_to_bigquery',
    python_callable=load_to_bigquery,
    dag=dag,
)

run_dbt_task = PythonOperator(
    task_id='run_dbt_transformations',
    python_callable=run_dbt_transformations,
    dag=dag,
)

train_ml_task = PythonOperator(
    task_id='train_ml_models',
    python_callable=train_ml_models,
    dag=dag,
)

# Task dependencies
collect_data_task >> upload_to_gcs_task >> load_to_bigquery_task >> run_dbt_task >> train_ml_task
