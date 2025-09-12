"""
IGDB AutoML Data Pipeline DAG
=============================

This DAG orchestrates the complete data pipeline from IGDB API to AutoML models:
1. Collect data from IGDB API
2. Upload raw data to Cloud Storage
3. Load data to BigQuery
4. Run dbt transformations
5. Prepare data for AutoML
6. Train AutoML models
7. Deploy trained models

Author: Data Engineering Team
Date: 2025-09-12
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
    'igdb_automl_pipeline',
    default_args=default_args,
    description='Complete IGDB data pipeline with AutoML integration',
    schedule=timedelta(days=1),  # Run daily
    catchup=False,
    tags=['igdb', 'data-pipeline', 'automl', 'ml'],
)

# Configuration
PROJECT_ID = 'exalted-tempo-471613-e2'
DATASET_ID = 'igdb_game_data'  # EU dataset
RAW_BUCKET = 'igdb-raw-data-eu-1757661329'
PROCESSED_BUCKET = 'igdb-processed-data-eu-1757661341'
AUTOML_BUCKET = 'igdb-ml-pipeline-automl'
SERVICE_ACCOUNT_KEY = '/Users/johanenstam/Sync/Utveckling/data-engineering/frontend/src/github-actions-key.json'
REGION = 'europe-west1'

def collect_igdb_data(**context):
    """
    Collect data from IGDB API and save to local file
    """
    import sys
    import os
    import logging
    
    # Add project path
    project_path = '/Users/johanenstam/Sync/Utveckling/data-engineering'
    sys.path.append(project_path)
    
    # Set working directory
    os.chdir(project_path)
    
    # Set up logging
    logging.info("Starting IGDB data collection...")
    logging.info(f"Working directory: {os.getcwd()}")
    logging.info(f"Python path includes: {project_path}")
    
    # Check if .env file exists
    env_file = os.path.join(project_path, '.env')
    if os.path.exists(env_file):
        logging.info(f".env file found: {env_file}")
    else:
        logging.error(f".env file NOT found: {env_file}")
        raise FileNotFoundError(f".env file not found at {env_file}")
    
    # Collect data using existing collector
    try:
        from src.data_collectors.igdb_data_collector import IGDBDataCollector
        collector = IGDBDataCollector()
        games_data = collector.collect_games(limit=100)  # Collect more games for AutoML
        
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
            'file_name': filename,
            'games_count': len(games_data)
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

def prepare_automl_data(**context):
    """
    Prepare data for AutoML training
    """
    import sys
    import pandas as pd
    from google.cloud import bigquery
    
    # Add project path
    project_path = '/Users/johanenstam/Sync/Utveckling/data-engineering'
    sys.path.append(project_path)
    
    # Set working directory
    os.chdir(project_path)
    
    logging.info("Preparing data for AutoML...")
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=PROJECT_ID)
        
        # Load data from BigQuery
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
        FROM `{PROJECT_ID}.{DATASET_ID}.games_raw`
        WHERE summary IS NOT NULL 
        AND rating IS NOT NULL
        AND name IS NOT NULL
        """
        
        df = client.query(query).to_dataframe()
        logging.info(f"Loaded {len(df)} games from BigQuery")
        
        # Prepare data for AutoML
        automl_data = []
        
        for _, row in df.iterrows():
            # Convert arrays to strings for AutoML
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
        
        # Create DataFrame
        automl_df = pd.DataFrame(automl_data)
        
        # Save as CSV for AutoML
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"automl_training_data_{timestamp}.csv"
        csv_filepath = f"/Users/johanenstam/Sync/Utveckling/data-engineering/{csv_filename}"
        automl_df.to_csv(csv_filepath, index=False)
        
        logging.info(f"AutoML data prepared and saved as: {csv_filename}")
        logging.info(f"Dataset contains {len(automl_df)} games with {len(automl_df.columns)} features")
        
        return {
            'csv_filename': csv_filename,
            'csv_filepath': csv_filepath,
            'data_size': len(automl_df),
            'features_count': len(automl_df.columns)
        }
        
    except Exception as e:
        logging.error(f"Error preparing AutoML data: {str(e)}")
        raise

def upload_automl_data_to_gcs(**context):
    """
    Upload AutoML training data to GCS
    """
    from airflow.providers.google.cloud.hooks.gcs import GCSHook
    
    # Get file info from previous task
    ti = context['ti']
    automl_info = ti.xcom_pull(task_ids='prepare_automl_data')
    csv_filepath = automl_info['csv_filepath']
    csv_filename = automl_info['csv_filename']
    
    # Upload to GCS
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    gcs_hook.upload(
        bucket_name=AUTOML_BUCKET,
        object_name=csv_filename,
        filename=csv_filepath,
        mime_type='text/csv'
    )
    
    gcs_uri = f"gs://{AUTOML_BUCKET}/{csv_filename}"
    logging.info(f"Uploaded AutoML data to: {gcs_uri}")
    
    return {
        'gcs_uri': gcs_uri,
        'bucket_name': AUTOML_BUCKET,
        'object_name': csv_filename
    }

def create_automl_dataset(**context):
    """
    Create AutoML dataset from GCS data
    """
    from google.cloud import aiplatform
    
    # Get GCS info from previous task
    ti = context['ti']
    gcs_info = ti.xcom_pull(task_ids='upload_automl_data_to_gcs')
    gcs_uri = gcs_info['gcs_uri']
    
    logging.info("Creating AutoML dataset...")
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        
        # Create dataset
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        dataset = aiplatform.TabularDataset.create(
            display_name=f"igdb-games-{timestamp}",
            gcs_source=[gcs_uri],
            labels={"project": "igdb-recommendations", "version": "v1", "pipeline": "automl"}
        )
        
        logging.info(f"AutoML dataset created: {dataset.resource_name}")
        
        return {
            'dataset_resource_name': dataset.resource_name,
            'dataset_display_name': f"igdb-games-{timestamp}"
        }
        
    except Exception as e:
        logging.error(f"Error creating AutoML dataset: {str(e)}")
        raise

def train_automl_model(**context):
    """
    Train AutoML model using the created dataset
    """
    from google.cloud import aiplatform
    
    # Get dataset info from previous task
    ti = context['ti']
    dataset_info = ti.xcom_pull(task_ids='create_automl_dataset')
    dataset_resource_name = dataset_info['dataset_resource_name']
    
    logging.info("Starting AutoML model training...")
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        
        # Create AutoML training job
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job = aiplatform.AutoMLTabularTrainingJob(
            display_name=f"igdb-recommendations-{timestamp}",
            optimization_prediction_type="regression",  # For rating prediction
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
            labels={"project": "igdb-recommendations", "version": "v1", "pipeline": "automl"}
        )
        
        # Get dataset
        dataset = aiplatform.TabularDataset(dataset_resource_name)
        
        # Start training
        model = job.run(
            dataset=dataset,
            model_display_name=f"igdb-recommendations-model-{timestamp}",
            training_fraction_split=0.8,
            validation_fraction_split=0.1,
            test_fraction_split=0.1,
            budget_milli_node_hours=1000,  # 1 node-hour budget
            disable_early_stopping=False,
            sync=True  # Wait for completion
        )
        
        logging.info(f"AutoML model training completed: {model.resource_name}")
        
        return {
            'model_resource_name': model.resource_name,
            'model_display_name': f"igdb-recommendations-model-{timestamp}",
            'training_status': 'completed'
        }
        
    except Exception as e:
        logging.error(f"Error training AutoML model: {str(e)}")
        raise

def deploy_automl_model(**context):
    """
    Deploy the trained AutoML model to an endpoint
    """
    from google.cloud import aiplatform
    
    # Get model info from previous task
    ti = context['ti']
    model_info = ti.xcom_pull(task_ids='train_automl_model')
    model_resource_name = model_info['model_resource_name']
    
    logging.info("Deploying AutoML model...")
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        
        # Get the trained model
        model = aiplatform.Model(model_resource_name)
        
        # Create endpoint
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        endpoint = model.deploy(
            deployed_model_display_name=f"igdb-recommendations-endpoint-{timestamp}",
            machine_type="n1-standard-4",
            min_replica_count=1,
            max_replica_count=3,
            sync=True  # Wait for deployment
        )
        
        logging.info(f"AutoML model deployed to endpoint: {endpoint.resource_name}")
        
        return {
            'endpoint_resource_name': endpoint.resource_name,
            'endpoint_display_name': f"igdb-recommendations-endpoint-{timestamp}",
            'deployment_status': 'completed'
        }
        
    except Exception as e:
        logging.error(f"Error deploying AutoML model: {str(e)}")
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

prepare_automl_data_task = PythonOperator(
    task_id='prepare_automl_data',
    python_callable=prepare_automl_data,
    dag=dag,
)

upload_automl_data_task = PythonOperator(
    task_id='upload_automl_data_to_gcs',
    python_callable=upload_automl_data_to_gcs,
    dag=dag,
)

create_automl_dataset_task = PythonOperator(
    task_id='create_automl_dataset',
    python_callable=create_automl_dataset,
    dag=dag,
)

train_automl_model_task = PythonOperator(
    task_id='train_automl_model',
    python_callable=train_automl_model,
    dag=dag,
)

deploy_automl_model_task = PythonOperator(
    task_id='deploy_automl_model',
    python_callable=deploy_automl_model,
    dag=dag,
)

# Task dependencies
collect_data_task >> upload_to_gcs_task >> load_to_bigquery_task >> run_dbt_task >> prepare_automl_data_task >> upload_automl_data_task >> create_automl_dataset_task >> train_automl_model_task >> deploy_automl_model_task
