"""
Test IGDB Data Pipeline DAG
===========================

Simplified version for testing the complete pipeline
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
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
    'test_igdb_pipeline',
    default_args=default_args,
    description='Test IGDB data pipeline',
    schedule=None,  # Manual trigger only
    catchup=False,
    tags=['test', 'igdb'],
)

def test_data_collection(**context):
    """Test data collection from IGDB API"""
    import sys
    sys.path.append('/Users/johanenstam/Sync/Utveckling/data-engineering')
    
    from src.data_collectors.igdb_data_collector import IGDBDataCollector
    
    logging.info("Testing IGDB data collection...")
    
    try:
        collector = IGDBDataCollector()
        games_data = collector.collect_games(limit=5)  # Small test
        
        logging.info(f"Successfully collected {len(games_data)} games")
        
        # Save test data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_games_{timestamp}.json"
        filepath = f"/Users/johanenstam/Sync/Utveckling/data-engineering/data/raw/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(games_data, f, indent=2)
        
        logging.info(f"Test data saved to: {filename}")
        
        return {
            'status': 'success',
            'games_collected': len(games_data),
            'file_path': filepath
        }
        
    except Exception as e:
        logging.error(f"Error in test data collection: {str(e)}")
        raise

def test_dbt_connection(**context):
    """Test dbt connection and models"""
    logging.info("Testing dbt connection...")
    
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/johanenstam/Sync/Utveckling/data-engineering/frontend/src/github-actions-key.json'
        
        # Test dbt debug
        dbt_project_dir = '/Users/johanenstam/Sync/Utveckling/data-engineering/dbt_igdb_project/igdb_models'
        os.system(f"cd {dbt_project_dir} && dbt debug --profiles-dir ~/.dbt")
        
        logging.info("dbt connection test successful!")
        
        return {'status': 'success'}
        
    except Exception as e:
        logging.error(f"Error in dbt test: {str(e)}")
        raise

def test_gcp_connection(**context):
    """Test GCP connections"""
    logging.info("Testing GCP connections...")
    
    try:
        from google.cloud import storage
        from google.cloud import bigquery
        
        # Test Storage connection
        client = storage.Client()
        buckets = list(client.list_buckets())
        logging.info(f"Found {len(buckets)} GCS buckets")
        
        # Test BigQuery connection
        bq_client = bigquery.Client()
        datasets = list(bq_client.list_datasets())
        logging.info(f"Found {len(datasets)} BigQuery datasets")
        
        logging.info("GCP connection test successful!")
        
        return {'status': 'success'}
        
    except Exception as e:
        logging.error(f"Error in GCP test: {str(e)}")
        raise

# Task definitions
test_data_task = PythonOperator(
    task_id='test_data_collection',
    python_callable=test_data_collection,
    dag=dag,
)

test_dbt_task = PythonOperator(
    task_id='test_dbt_connection',
    python_callable=test_dbt_connection,
    dag=dag,
)

test_gcp_task = PythonOperator(
    task_id='test_gcp_connection',
    python_callable=test_gcp_connection,
    dag=dag,
)

# Task dependencies - run in parallel
[test_data_task, test_dbt_task, test_gcp_task]
