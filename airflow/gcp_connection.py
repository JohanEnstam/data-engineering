"""
GCP Connection Setup for Airflow
===============================

This script sets up the Google Cloud Platform connection for Airflow.
Run this after initializing Airflow to configure GCP access.
"""

import os
from airflow.models import Connection
from airflow.utils.session import create_session

def setup_gcp_connection():
    """Set up GCP connection for Airflow"""
    
    # GCP connection details
    conn_id = 'google_cloud_default'
    conn_type = 'google_cloud_platform'
    project_id = 'exalted-tempo-471613-e2'
    key_path = '/Users/johanenstam/Sync/Utveckling/data-engineering/frontend/src/github-actions-key.json'
    
    # Create connection
    with create_session() as session:
        # Check if connection already exists
        existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
        
        if existing_conn:
            print(f"Connection {conn_id} already exists. Updating...")
            existing_conn.conn_type = conn_type
            existing_conn.extra = f'{{"extra__google_cloud_platform__key_path": "{key_path}", "extra__google_cloud_platform__project_id": "{project_id}"}}'
        else:
            print(f"Creating new connection {conn_id}...")
            new_conn = Connection(
                conn_id=conn_id,
                conn_type=conn_type,
                extra=f'{{"extra__google_cloud_platform__key_path": "{key_path}", "extra__google_cloud_platform__project_id": "{project_id}"}}'
            )
            session.add(new_conn)
        
        session.commit()
        print(f"GCP connection {conn_id} configured successfully!")

if __name__ == "__main__":
    setup_gcp_connection()
