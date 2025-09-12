"""
Test AutoML Pipeline DAG
========================

Simple test DAG to verify AutoML integration works
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
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
    'test_automl_pipeline',
    default_args=default_args,
    description='Test AutoML integration',
    schedule=None,  # Manual trigger only
    catchup=False,
    tags=['test', 'automl'],
)

# Configuration
PROJECT_ID = 'exalted-tempo-471613-e2'
REGION = 'europe-west1'

def test_automl_connection(**context):
    """
    Test AutoML connection and basic functionality
    """
    import sys
    import os
    from google.cloud import aiplatform
    
    # Add project path
    project_path = '/Users/johanenstam/Sync/Utveckling/data-engineering'
    sys.path.append(project_path)
    
    # Set working directory
    os.chdir(project_path)
    
    logging.info("Testing AutoML connection...")
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        logging.info("✅ Vertex AI initialized successfully")
        
        # List existing datasets
        datasets = aiplatform.TabularDataset.list()
        logging.info(f"📊 Found {len(datasets)} existing datasets")
        
        # Test AutoML job configuration
        job = aiplatform.AutoMLTabularTrainingJob(
            display_name=f"test-automl-job-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            optimization_prediction_type="regression",
            optimization_objective="minimize-mae",
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
        
        logging.info("✅ AutoML job configuration successful")
        
        return {
            'status': 'success',
            'datasets_count': len(datasets),
            'job_configured': True
        }
        
    except Exception as e:
        logging.error(f"❌ AutoML test failed: {str(e)}")
        raise

def test_bigquery_connection(**context):
    """
    Test BigQuery connection
    """
    from google.cloud import bigquery
    
    logging.info("Testing BigQuery connection...")
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=PROJECT_ID)
        
        # Test query
        query = f"""
        SELECT COUNT(*) as total_games
        FROM `{PROJECT_ID}.igdb_game_data.games_raw`
        """
        
        result = client.query(query).to_dataframe()
        total_games = result['total_games'].iloc[0]
        
        logging.info(f"✅ BigQuery connection successful")
        logging.info(f"📊 Found {total_games} games in BigQuery")
        
        return {
            'status': 'success',
            'total_games': int(total_games)
        }
        
    except Exception as e:
        logging.error(f"❌ BigQuery test failed: {str(e)}")
        raise

# Task definitions
test_automl_task = PythonOperator(
    task_id='test_automl_connection',
    python_callable=test_automl_connection,
    dag=dag,
)

test_bigquery_task = PythonOperator(
    task_id='test_bigquery_connection',
    python_callable=test_bigquery_connection,
    dag=dag,
)

# Task dependencies
test_automl_task >> test_bigquery_task
