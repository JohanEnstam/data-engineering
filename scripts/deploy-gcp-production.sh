#!/bin/bash
"""
GCP Production Deployment Script
Automatiserar hela deployment processen till GCP
"""

set -e  # Exit on any error

# Konfiguration
PROJECT_ID="exalted-tempo-471613-e2"
REGION="europe-west1"
REGISTRY="gcr.io"

# Colors för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if venv is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_error "Virtual environment is not activated!"
        log_info "Please run: source venv/bin/activate"
        exit 1
    fi
    log_success "Virtual environment is activated: $VIRTUAL_ENV"
}

# Check if gcloud is authenticated
check_gcloud_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        log_error "Not authenticated with gcloud!"
        log_info "Please run: gcloud auth login"
        exit 1
    fi
    log_success "Authenticated with gcloud"
}

# Set project
set_project() {
    log_info "Setting GCP project to $PROJECT_ID"
    gcloud config set project $PROJECT_ID
    log_success "Project set to $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required GCP APIs..."
    
    APIs=(
        "composer.googleapis.com"
        "cloudfunctions.googleapis.com"
        "run.googleapis.com"
        "bigquery.googleapis.com"
        "storage.googleapis.com"
        "aiplatform.googleapis.com"
        "secretmanager.googleapis.com"
        "cloudbuild.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${APIs[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable $api
    done
    
    log_success "All APIs enabled"
}

# Deploy Cloud Composer
deploy_composer() {
    log_info "Deploying Cloud Composer..."
    
    # Check if composer environment already exists
    if gcloud composer environments describe igdb-data-pipeline --location=europe-west1-a &>/dev/null; then
        log_warning "Composer environment already exists, skipping creation"
    else
        log_info "Creating Composer environment (this takes 20-30 minutes)..."
        python gcp/cloud_composer_setup.py
        
        # Wait for environment to be ready
        log_info "Waiting for Composer environment to be ready..."
        while true; do
            STATE=$(gcloud composer environments describe igdb-data-pipeline --location=europe-west1-a --format='value(state)' 2>/dev/null || echo "CREATING")
            if [[ "$STATE" == "RUNNING" ]]; then
                log_success "Composer environment is ready!"
                break
            elif [[ "$STATE" == "ERROR" ]]; then
                log_error "Composer environment creation failed!"
                exit 1
            else
                log_info "Composer environment state: $STATE, waiting..."
                sleep 30
            fi
        done
    fi
    
    # Set up permissions
    log_info "Setting up Composer permissions..."
    COMPOSER_SA="composer-service-account@$PROJECT_ID.iam.gserviceaccount.com"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$COMPOSER_SA" \
        --role="roles/bigquery.admin" || true
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$COMPOSER_SA" \
        --role="roles/storage.admin" || true
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$COMPOSER_SA" \
        --role="roles/aiplatform.user" || true
    
    # Upload DAGs
    log_info "Uploading DAGs to Composer..."
    COMPOSER_BUCKET=$(gcloud composer environments describe igdb-data-pipeline --location=europe-west1-a --format='value(config.dagGcsPrefix)' | sed 's|/dags||')
    gsutil cp airflow/dags/*.py gs://$COMPOSER_BUCKET/dags/
    
    log_success "Cloud Composer deployed successfully"
}

# Deploy Cloud Functions
deploy_functions() {
    log_info "Deploying Cloud Functions..."
    
    # Create secrets if they don't exist
    if ! gcloud secrets describe igdb-client-id &>/dev/null; then
        log_warning "IGDB Client ID secret not found. Please create it:"
        log_info "echo 'your-twitch-client-id' | gcloud secrets create igdb-client-id --data-file=-"
        read -p "Press Enter after creating the secret..."
    fi
    
    if ! gcloud secrets describe igdb-client-secret &>/dev/null; then
        log_warning "IGDB Client Secret secret not found. Please create it:"
        log_info "echo 'your-twitch-client-secret' | gcloud secrets create igdb-client-secret --data-file=-"
        read -p "Press Enter after creating the secret..."
    fi
    
    # Deploy function
    cd gcp
    zip -r igdb-data-collector.zip . &>/dev/null
    
    gcloud functions deploy igdb-data-collector \
        --runtime python39 \
        --trigger-http \
        --allow-unauthenticated \
        --memory 1024MB \
        --timeout 540s \
        --region $REGION \
        --source . \
        --entry-point collect_igdb_data \
        --set-secrets IGDB_CLIENT_ID=igdb-client-id:latest,IGDB_CLIENT_SECRET=igdb-client-secret:latest
    
    cd ..
    
    # Create scheduler job
    log_info "Creating Cloud Scheduler job..."
    gcloud scheduler jobs create http igdb-data-collection-schedule \
        --schedule="0 2 * * *" \
        --uri="https://$REGION-$PROJECT_ID.cloudfunctions.net/igdb-data-collector" \
        --http-method=POST \
        --time-zone="Europe/Stockholm" \
        --headers="Content-Type=application/json" \
        --message-body='{"trigger":"scheduled","games_limit":1000}' \
        || log_warning "Scheduler job may already exist"
    
    log_success "Cloud Functions deployed successfully"
}

# Deploy Cloud Run services
deploy_cloud_run() {
    log_info "Deploying Cloud Run services..."
    
    # Build and push backend
    log_info "Building backend Docker image..."
    docker build -f Dockerfile -t $REGISTRY/$PROJECT_ID/igdb-backend-prod:latest .
    docker push $REGISTRY/$PROJECT_ID/igdb-backend-prod:latest
    
    # Deploy backend
    log_info "Deploying backend to Cloud Run..."
    gcloud run deploy igdb-backend-prod \
        --image $REGISTRY/$PROJECT_ID/igdb-backend-prod:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8000 \
        --memory 2Gi \
        --cpu 2 \
        --min-instances 1 \
        --max-instances 20 \
        --set-env-vars="ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID"
    
    # Build and push frontend
    log_info "Building frontend Docker image..."
    docker build -f frontend/Dockerfile -t $REGISTRY/$PROJECT_ID/igdb-frontend-prod:latest ./frontend
    docker push $REGISTRY/$PROJECT_ID/igdb-frontend-prod:latest
    
    # Deploy frontend
    log_info "Deploying frontend to Cloud Run..."
    BACKEND_URL=$(gcloud run services describe igdb-backend-prod --region=$REGION --format='value(status.url)')
    
    gcloud run deploy igdb-frontend-prod \
        --image $REGISTRY/$PROJECT_ID/igdb-frontend-prod:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 3000 \
        --memory 1Gi \
        --cpu 1 \
        --min-instances 1 \
        --max-instances 10 \
        --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"
    
    log_success "Cloud Run services deployed successfully"
    
    # Get service URLs
    BACKEND_URL=$(gcloud run services describe igdb-backend-prod --region=$REGION --format='value(status.url)')
    FRONTEND_URL=$(gcloud run services describe igdb-frontend-prod --region=$REGION --format='value(status.url)')
    
    log_info "Service URLs:"
    log_info "Backend: $BACKEND_URL"
    log_info "Frontend: $FRONTEND_URL"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Create budget alert
    log_info "Creating budget alert..."
    gcloud billing budgets create \
        --billing-account=$(gcloud billing accounts list --format='value(name)' | head -1) \
        --display-name="IGDB Pipeline Budget Alert" \
        --budget-amount=500USD \
        --threshold-rule=percent=80 \
        --threshold-rule=percent=100 \
        --notification-rule=email=johanenstam@gmail.com \
        || log_warning "Budget alert may already exist"
    
    # Create monitoring policies
    log_info "Creating monitoring policies..."
    gcloud alpha monitoring policies create \
        --policy-from-file=monitoring/cloud-run-alerts.yaml \
        || log_warning "Monitoring policies may already exist"
    
    log_success "Monitoring setup completed"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Wait for services to be ready
    sleep 30
    
    # Test backend
    BACKEND_URL=$(gcloud run services describe igdb-backend-prod --region=$REGION --format='value(status.url)')
    log_info "Testing backend health at $BACKEND_URL/health"
    
    if curl -f "$BACKEND_URL/health" &>/dev/null; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Test frontend
    FRONTEND_URL=$(gcloud run services describe igdb-frontend-prod --region=$REGION --format='value(status.url)')
    log_info "Testing frontend at $FRONTEND_URL"
    
    if curl -f "$FRONTEND_URL" &>/dev/null; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
    
    log_success "All smoke tests passed!"
}

# Main deployment function
main() {
    log_info "Starting GCP Production Deployment"
    log_info "Project: $PROJECT_ID"
    log_info "Region: $REGION"
    echo "=================================="
    
    # Pre-flight checks
    check_venv
    check_gcloud_auth
    set_project
    
    # Deployment steps
    enable_apis
    deploy_composer
    deploy_functions
    deploy_cloud_run
    setup_monitoring
    run_smoke_tests
    
    log_success "🎉 GCP Production Deployment Completed Successfully!"
    
    # Final summary
    BACKEND_URL=$(gcloud run services describe igdb-backend-prod --region=$REGION --format='value(status.url)')
    FRONTEND_URL=$(gcloud run services describe igdb-frontend-prod --region=$REGION --format='value(status.url)')
    
    echo "=================================="
    log_info "Deployment Summary:"
    log_info "Backend URL: $BACKEND_URL"
    log_info "Frontend URL: $FRONTEND_URL"
    log_info "Cloud Composer: https://console.cloud.google.com/composer/environments"
    log_info "Cloud Functions: https://console.cloud.google.com/functions"
    log_info "Cloud Run: https://console.cloud.google.com/run"
    echo "=================================="
    
    log_info "Next steps:"
    log_info "1. Test the application at $FRONTEND_URL"
    log_info "2. Monitor costs in GCP Console"
    log_info "3. Set up custom domain (optional)"
    log_info "4. Configure additional monitoring alerts"
}

# Run main function
main "$@"
