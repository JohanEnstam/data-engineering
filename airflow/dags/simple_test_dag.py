"""
Simple Test DAG
===============

A minimal DAG to test Airflow functionality without external dependencies.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

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
    'simple_test_dag',
    default_args=default_args,
    description='Simple test DAG to verify Airflow functionality',
    schedule=None,  # Manual trigger only
    catchup=False,
    tags=['test', 'simple'],
)

def simple_python_task(**context):
    """
    Simple Python task that just prints and returns data
    """
    import logging
    import os
    
    logging.info("Starting simple Python task...")
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Python path: {os.sys.path[:3]}")  # First 3 entries
    
    # Simple data processing
    data = {
        'message': 'Hello from Airflow!',
        'timestamp': datetime.now().isoformat(),
        'working_dir': os.getcwd(),
        'python_version': os.sys.version
    }
    
    logging.info(f"Task completed successfully: {data}")
    return data

def test_igdb_import(**context):
    """
    Test if we can import IGDB collector
    """
    import sys
    import logging
    import os
    
    logging.info("Testing IGDB import...")
    
    # Add project path
    project_path = '/Users/johanenstam/Sync/Utveckling/data-engineering'
    if project_path not in sys.path:
        sys.path.append(project_path)
    
    try:
        # Test import
        from src.data_collectors.igdb_data_collector import IGDBDataCollector
        logging.info("✅ IGDB collector imported successfully!")
        
        # Test instantiation
        collector = IGDBDataCollector()
        logging.info("✅ IGDB collector instantiated successfully!")
        
        return {
            'status': 'success',
            'message': 'IGDB collector works in Airflow'
        }
        
    except Exception as e:
        logging.error(f"❌ Error with IGDB collector: {str(e)}")
        raise

# Task definitions
simple_task = PythonOperator(
    task_id='simple_python_task',
    python_callable=simple_python_task,
    dag=dag,
)

test_igdb_task = PythonOperator(
    task_id='test_igdb_import',
    python_callable=test_igdb_import,
    dag=dag,
)

bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello from Bash!" && pwd && ls -la .env',
    dag=dag,
)

# Task dependencies
simple_task >> test_igdb_task >> bash_task
