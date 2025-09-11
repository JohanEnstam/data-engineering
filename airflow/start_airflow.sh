#!/bin/bash

# Airflow Startup Script
# ======================

echo "🚀 Starting Airflow for IGDB Data Pipeline..."

# Set environment variables
export AIRFLOW_HOME=/Users/johanenstam/Sync/Utveckling/data-engineering/airflow
export GOOGLE_APPLICATION_CREDENTIALS=/Users/johanenstam/Sync/Utveckling/data-engineering/frontend/src/github-actions-key.json

# Activate virtual environment
source /Users/johanenstam/Sync/Utveckling/data-engineering/venv/bin/activate

# Generate secure keys
echo "🔐 Generating secure keys..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")

# Update airflow.cfg with generated keys
sed -i.bak "s/secret_key = your-secret-key-here/secret_key = $SECRET_KEY/" $AIRFLOW_HOME/airflow.cfg
sed -i.bak "s/jwt_secret = your-jwt-secret-key-here/jwt_secret = $JWT_SECRET/" $AIRFLOW_HOME/airflow.cfg

# Initialize Airflow database (first time only)
if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    echo "📊 Initializing Airflow database..."
    airflow db migrate
fi

# Set up GCP connection
echo "🔗 Setting up GCP connection..."
python $AIRFLOW_HOME/gcp_connection.py

# Start Airflow in standalone mode (includes webserver + scheduler)
echo "🌐 Starting Airflow in standalone mode on http://localhost:8080..."
echo "📱 Web UI: http://localhost:8080"
echo "🔑 Default login: admin / admin"
echo ""
echo "Press Ctrl+C to stop Airflow"
echo ""

airflow standalone
