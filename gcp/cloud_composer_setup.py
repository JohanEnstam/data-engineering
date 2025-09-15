#!/usr/bin/env python3
"""
Cloud Composer Setup Script för IGDB Pipeline
Sätter upp Managed Airflow i GCP med vår befintliga DAG
"""

import os
import json
from datetime import datetime
from google.cloud import composer_v1
from google.cloud.composer_v1.types import Environment, NodeCount, SoftwareConfig
from google.cloud import storage
from google.cloud import bigquery

# Konfiguration
PROJECT_ID = "exalted-tempo-471613-e2"
REGION = "europe-west1"
COMPOSER_ENVIRONMENT_NAME = "igdb-data-pipeline"
COMPOSER_LOCATION = f"{REGION}-a"  # Composer kräver specifik zon

def create_composer_environment():
    """Skapa Cloud Composer environment för Airflow"""
    
    print("🚀 Skapar Cloud Composer environment...")
    
    # Initiera Composer client
    client = composer_v1.EnvironmentsClient()
    
    # Environment konfiguration
    environment = Environment(
        name=f"projects/{PROJECT_ID}/locations/{COMPOSER_LOCATION}/environments/{COMPOSER_ENVIRONMENT_NAME}",
        config=Environment.Config(
            node_count=NodeCount(worker=3),  # 3 worker nodes för skalning
            software_config=SoftwareConfig(
                image_version="composer-2.4.0-airflow-2.7.3",  # Senaste stabila version
                python_version="3",
                airflow_config_overrides={
                    "core-dags_are_paused_at_creation": "False",
                    "core-max_active_tasks_per_dag": "16",
                    "core-parallelism": "32",
                    "webserver-web_server_master_timeout": "120",
                    "webserver-web_server_worker_timeout": "120",
                },
                pypi_packages={
                    "google-cloud-bigquery": ">=3.11.0",
                    "google-cloud-storage": ">=2.10.0",
                    "google-cloud-aiplatform": ">=1.35.0",
                    "pandas": ">=1.5.0",
                    "requests": ">=2.28.0",
                    "python-dotenv": ">=0.19.0",
                },
                env_variables={
                    "AIRFLOW_VAR_PROJECT_ID": PROJECT_ID,
                    "AIRFLOW_VAR_REGION": REGION,
                    "AIRFLOW_VAR_DATASET_ID": "igdb_game_data",
                    "AIRFLOW_VAR_RAW_BUCKET": "igdb-raw-data-eu-1757661329",
                    "AIRFLOW_VAR_PROCESSED_BUCKET": "igdb-processed-data-eu-1757661341",
                    "AIRFLOW_VAR_AUTOML_BUCKET": "igdb-ml-pipeline-automl",
                }
            ),
            environment_size="ENVIRONMENT_SIZE_MEDIUM",  # För production workload
            node_config=Environment.NodeConfig(
                machine_type="n1-standard-2",  # 2 vCPU, 7.5GB RAM per node
                disk_size_gb=100,
                disk_type="pd-standard",
                network="default",
                subnetwork="default",
                service_account=f"composer-service-account@{PROJECT_ID}.iam.gserviceaccount.com"
            )
        ),
        labels={
            "project": "igdb-recommendations",
            "environment": "production",
            "created_by": "data-engineering-team"
        }
    )
    
    # Skapa environment
    operation = client.create_environment(
        parent=f"projects/{PROJECT_ID}/locations/{COMPOSER_LOCATION}",
        environment=environment
    )
    
    print(f"✅ Cloud Composer environment skapas...")
    print(f"📍 Location: {COMPOSER_LOCATION}")
    print(f"🏷️ Name: {COMPOSER_ENVIRONMENT_NAME}")
    print(f"⏱️ Detta kan ta 20-30 minuter...")
    
    return operation

def setup_composer_permissions():
    """Sätt upp nödvändiga permissions för Composer"""
    
    print("\n🔐 Konfigurerar Composer permissions...")
    
    # Service account som Composer kommer använda
    composer_sa = f"composer-service-account@{PROJECT_ID}.iam.gserviceaccount.com"
    
    # Nödvändiga roller för Composer
    roles = [
        "roles/bigquery.admin",
        "roles/storage.admin", 
        "roles/aiplatform.user",
        "roles/cloudsql.client",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter",
        "roles/composer.worker"
    ]
    
    print(f"📋 Service Account: {composer_sa}")
    print("📋 Nödvändiga roller:")
    for role in roles:
        print(f"  - {role}")
    
    print("\n💡 Kör följande kommandon för att sätta upp permissions:")
    print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} \\")
    print(f"    --member='serviceAccount:{composer_sa}' \\")
    print(f"    --role='roles/bigquery.admin'")
    
    for role in roles[1:]:  # Resten av rollerna
        print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} \\")
        print(f"    --member='serviceAccount:{composer_sa}' \\")
        print(f"    --role='{role}'")
    
    return composer_sa, roles

def upload_dags_to_composer():
    """Ladda upp våra DAGs till Composer"""
    
    print("\n📁 Förbereder DAG upload till Composer...")
    
    # Composer DAG bucket kommer skapas automatiskt
    dag_bucket = f"{PROJECT_ID}-composer-bucket"
    dag_folder = f"dags"
    
    # DAGs att ladda upp
    dag_files = [
        "airflow/dags/igdb_automl_pipeline.py",
        "airflow/dags/igdb_data_pipeline.py"
    ]
    
    print(f"📦 DAG Bucket: {dag_bucket}")
    print(f"📁 DAG Folder: {dag_folder}")
    print("📋 DAGs att ladda upp:")
    for dag_file in dag_files:
        print(f"  - {dag_file}")
    
    print("\n💡 Efter att Composer är skapat, kör:")
    print(f"gsutil cp airflow/dags/*.py gs://{dag_bucket}/dags/")
    
    return dag_bucket, dag_folder, dag_files

def create_composer_monitoring():
    """Sätt upp monitoring för Composer"""
    
    print("\n📊 Konfigurerar Composer monitoring...")
    
    # Monitoring alerts för Composer
    alerts = [
        {
            "name": "composer-dag-failure",
            "description": "Alert när DAG körningar misslyckas",
            "metric": "airflow.dagrun.failed",
            "threshold": 1
        },
        {
            "name": "composer-task-failure", 
            "description": "Alert när tasks misslyckas",
            "metric": "airflow.task.failed",
            "threshold": 5
        },
        {
            "name": "composer-environment-health",
            "description": "Alert när Composer environment är unhealthy",
            "metric": "composer.environment.health",
            "threshold": 0.5
        }
    ]
    
    print("📋 Monitoring alerts:")
    for alert in alerts:
        print(f"  - {alert['name']}: {alert['description']}")
    
    return alerts

def main():
    """Huvudfunktion för Cloud Composer setup"""
    
    print("🎮 IGDB Cloud Composer Setup")
    print("=" * 50)
    
    try:
        # Steg 1: Skapa Composer environment
        print("\n🚀 STEG 1: Skapar Cloud Composer Environment")
        operation = create_composer_environment()
        
        # Steg 2: Sätt upp permissions
        print("\n🔐 STEG 2: Konfigurerar Permissions")
        composer_sa, roles = setup_composer_permissions()
        
        # Steg 3: Förbered DAG upload
        print("\n📁 STEG 3: Förbereder DAG Upload")
        dag_bucket, dag_folder, dag_files = upload_dags_to_composer()
        
        # Steg 4: Sätt upp monitoring
        print("\n📊 STEG 4: Konfigurerar Monitoring")
        alerts = create_composer_monitoring()
        
        # Spara konfiguration
        config = {
            "project_id": PROJECT_ID,
            "region": REGION,
            "composer_location": COMPOSER_LOCATION,
            "environment_name": COMPOSER_ENVIRONMENT_NAME,
            "composer_sa": composer_sa,
            "required_roles": roles,
            "dag_bucket": dag_bucket,
            "dag_folder": dag_folder,
            "dag_files": dag_files,
            "monitoring_alerts": alerts,
            "created_at": datetime.now().isoformat(),
            "status": "setup_initiated"
        }
        
        with open("composer_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("\n🎉 Cloud Composer setup initierad!")
        print(f"⏱️ Environment skapas... (20-30 minuter)")
        print(f"📁 Konfiguration sparad i composer_config.json")
        
        print("\n📋 NÄSTA STEG:")
        print("1. Vänta tills Composer environment är klart")
        print("2. Kör permission setup kommandon")
        print("3. Ladda upp DAGs till Composer bucket")
        print("4. Testa DAG körning i Airflow UI")
        
        return config
        
    except Exception as e:
        print(f"❌ Fel vid Composer setup: {str(e)}")
        raise

if __name__ == "__main__":
    main()
