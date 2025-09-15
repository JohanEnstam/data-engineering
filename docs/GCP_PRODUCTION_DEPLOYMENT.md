# 🚀 GCP Production Deployment Guide

## ✅ **Status: Kostnadseffektiv GCP Pipeline för Kursprojekt**

**Vår situation:**
- 🎓 **Kursprojekt** - 4 veckor kvar, behöver fungerande pipeline för betyg
- 💰 **$300 free credits** - Vill inte bränna i onödan
- 🎯 **100 spel** - Nuvarande dataset, vill expandera senare
- 📚 **Lärande-fokus** - Vill förstå varje steg, inte bygga production system

**Vad vi har implementerat:**
- ✅ **Cloud Functions** - Serverless IGDB data collection
- ✅ **BigQuery** - Data warehouse för spel data
- ✅ **Cloud Run** - Containerized FastAPI + Next.js
- ✅ **Cloud Build CI/CD** - Automatisk deployment
- ✅ **Monitoring & Alerting** - Budget och performance alerts
- 🔄 **Cloud Composer** - Planerat för senare (när vi har fungerande grund)

---

## 🎯 **UPPDATERAD DEPLOYMENT ROADMAP**

### **Fas 1: Enkel Pipeline (1-2 dagar) - AKTUELL**

#### **1.1 Cloud Composer Setup**

```bash
# Aktivera venv först
source venv/bin/activate

# Aktivera nödvändiga APIs
gcloud services enable composer.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Kör Composer setup
python gcp/cloud_composer_setup.py

# Vänta tills environment är klart (20-30 min)
gcloud composer environments describe igdb-data-pipeline \
  --location=europe-west1-a \
  --format='value(state)'
```

**När Composer är klart:**
```bash
# Sätt upp permissions
COMPOSER_SA="composer-service-account@exalted-tempo-471613-e2.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
  --member="serviceAccount:$COMPOSER_SA" \
  --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
  --member="serviceAccount:$COMPOSER_SA" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
  --member="serviceAccount:$COMPOSER_SA" \
  --role="roles/aiplatform.user"

# Ladda upp DAGs
COMPOSER_BUCKET=$(gcloud composer environments describe igdb-data-pipeline \
  --location=europe-west1-a \
  --format='value(config.dagGcsPrefix)' | sed 's|/dags||')

gsutil cp airflow/dags/*.py gs://$COMPOSER_BUCKET/dags/
```

#### **1.2 Cloud Functions Setup**

```bash
# Aktivera Functions API
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Kör Functions setup
python gcp/cloud_functions.py

# Skapa secrets för IGDB credentials
echo "your-twitch-client-id" | gcloud secrets create igdb-client-id --data-file=-
echo "your-twitch-client-secret" | gcloud secrets create igdb-client-secret --data-file=-

# Deploy function
cd gcp
zip -r igdb-data-collector.zip .
gcloud functions deploy igdb-data-collector \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 1024MB \
  --timeout 540s \
  --region europe-west1 \
  --source . \
  --entry-point collect_igdb_data \
  --set-secrets IGDB_CLIENT_ID=igdb-client-id:latest,IGDB_CLIENT_SECRET=igdb-client-secret:latest
```

#### **1.3 Vertex AI AutoML Setup**

```bash
# Aktivera Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Kör AutoML setup med befintlig data
python src/automl_setup.py

# Detta kommer:
# 1. Ladda data från BigQuery
# 2. Förbereda för AutoML
# 3. Skapa dataset i Vertex AI
# 4. Starta träningsjobb
```

### **Fas 2: Application Deployment (1-2 dagar)**

#### **2.1 Cloud Run Backend**

```bash
# Bygg och push backend image
docker build -f Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-backend-prod:latest .
docker push gcr.io/exalted-tempo-471613-e2/igdb-backend-prod:latest

# Deploy till Cloud Run
gcloud run deploy igdb-backend-prod \
  --image gcr.io/exalted-tempo-471613-e2/igdb-backend-prod:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 20 \
  --set-env-vars="ENVIRONMENT=production,PROJECT_ID=exalted-tempo-471613-e2"
```

#### **2.2 Cloud Run Frontend**

```bash
# Bygg och push frontend image
docker build -f frontend/Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-frontend-prod:latest ./frontend
docker push gcr.io/exalted-tempo-471613-e2/igdb-frontend-prod:latest

# Deploy till Cloud Run
gcloud run deploy igdb-frontend-prod \
  --image gcr.io/exalted-tempo-471613-e2/igdb-frontend-prod:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://igdb-backend-prod-xxx-ew.a.run.app"
```

### **Fas 3: CI/CD Pipeline (1 dag)**

#### **3.1 GitHub Secrets Setup**

**Gå till GitHub → Settings → Secrets and variables → Actions**

**Repository Secrets:**
```
IGDB_CLIENT_ID: [din_twitch_client_id]
IGDB_CLIENT_SECRET: [din_twitch_client_secret]
GCP_PROJECT_ID: exalted-tempo-471613-e2
```

**Environment Secrets (för staging och production):**
```
GCP_SA_KEY: [din_service_account_key_json]
```

#### **3.2 Aktivera GitHub Actions**

```bash
# Committa nya workflow
git add .github/workflows/gcp-deployment.yml
git add gcp/
git add docs/GCP_PRODUCTION_DEPLOYMENT.md

git commit -m "feat: Add complete GCP production deployment pipeline

- Add Cloud Composer setup for managed Airflow
- Add Cloud Functions for serverless data collection  
- Add comprehensive CI/CD pipeline with staging/production
- Add monitoring and alerting configuration
- Add complete deployment documentation"

git push origin develop
```

### **Fas 4: Monitoring & Optimization (1 dag)**

#### **4.1 Budget Monitoring**

```bash
# Skapa budget alert
gcloud billing budgets create \
  --billing-account=$(gcloud billing accounts list --format='value(name)' | head -1) \
  --display-name="IGDB Pipeline Budget Alert" \
  --budget-amount=500USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100 \
  --notification-rule=email=johanenstam@gmail.com
```

#### **4.2 Performance Monitoring**

```bash
# Skapa monitoring alerts för Cloud Run
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/cloud-run-alerts.yaml
```

---

## 🏗️ **GCP PRODUCTION ARKITEKTUR**

### **📊 Data Flow:**

```
IGDB API → Cloud Functions → Cloud Storage → BigQuery → dbt → Vertex AI AutoML
    ↓
Cloud Composer (Airflow) → Orchestrerar hela pipeline
    ↓
Cloud Run (FastAPI + Next.js) → Serves recommendations
```

### **🔧 Services Overview:**

| Service | Purpose | Cost/Month | Scaling |
|---------|---------|------------|---------|
| **Cloud Composer** | Airflow orchestration | ~$300 | Auto |
| **Cloud Functions** | IGDB data collection | ~$5 | Serverless |
| **Cloud Storage** | Raw data storage | ~$10 | Unlimited |
| **BigQuery** | Data warehouse | ~$50 | Pay-per-use |
| **Vertex AI AutoML** | ML training | ~$20/training | On-demand |
| **Cloud Run** | App hosting | ~$30 | Auto |
| **Cloud Build** | CI/CD | ~$5 | Pay-per-build |

**Total Estimated Cost: ~$420/month**

---

## 🚀 **DEPLOYMENT COMMANDS**

### **Komplett Deployment (en gång):**

```bash
# Aktivera venv först
source venv/bin/activate

# 1. Sätt upp alla GCP services
python gcp/cloud_composer_setup.py
python gcp/cloud_functions.py
python src/automl_setup.py

# 2. Deploy applications
docker build -f Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-backend-prod:latest .
docker build -f frontend/Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-frontend-prod:latest ./frontend

docker push gcr.io/exalted-tempo-471613-e2/igdb-backend-prod:latest
docker push gcr.io/exalted-tempo-471613-e2/igdb-frontend-prod:latest

gcloud run deploy igdb-backend-prod --image gcr.io/exalted-tempo-471613-e2/igdb-backend-prod:latest --platform managed --region europe-west1 --allow-unauthenticated --port 8000 --memory 2Gi --cpu 2 --min-instances 1 --max-instances 20

gcloud run deploy igdb-frontend-prod --image gcr.io/exalted-tempo-471613-e2/igdb-frontend-prod:latest --platform managed --region europe-west1 --allow-unauthenticated --port 3000 --memory 1Gi --cpu 1 --min-instances 1 --max-instances 10

# 3. Aktivera CI/CD
git add .
git commit -m "feat: Deploy complete GCP production pipeline"
git push origin develop
```

### **Automatisk Deployment (CI/CD):**

**Staging (develop branch):**
- Push till `develop` → Automatisk deployment till staging
- URL: `https://igdb-frontend-staging-xxx-ew.a.run.app`

**Production (main branch):**
- Push till `main` → Automatisk deployment till production  
- URL: `https://igdb-frontend-prod-xxx-ew.a.run.app`

---

## 📋 **VERIFICATION CHECKLIST**

### **✅ Core Services:**
- [ ] Cloud Composer environment är aktivt
- [ ] Cloud Functions deployad och testad
- [ ] Vertex AI AutoML dataset skapat
- [ ] BigQuery tables populeras korrekt

### **✅ Applications:**
- [ ] Backend Cloud Run service är aktivt
- [ ] Frontend Cloud Run service är aktivt
- [ ] Health checks fungerar
- [ ] API endpoints svarar korrekt

### **✅ CI/CD:**
- [ ] GitHub Actions workflows körs
- [ ] Staging deployment fungerar
- [ ] Production deployment fungerar
- [ ] Secrets är korrekt konfigurerade

### **✅ Monitoring:**
- [ ] Budget alerts är aktiva
- [ ] Performance monitoring fungerar
- [ ] Error alerting är konfigurerat
- [ ] Logs är tillgängliga

---

## 🚨 **TROUBLESHOOTING**

### **"Cloud Composer environment failed"**
```bash
# Kontrollera status
gcloud composer environments describe igdb-data-pipeline --location=europe-west1-a

# Kontrollera logs
gcloud logging read "resource.type=composer_environment" --limit=50
```

### **"Cloud Functions timeout"**
```bash
# Öka timeout
gcloud functions deploy igdb-data-collector --timeout 900s

# Kontrollera logs
gcloud functions logs read igdb-data-collector --limit=50
```

### **"Cloud Run deployment failed"**
```bash
# Kontrollera service status
gcloud run services describe igdb-backend-prod --region=europe-west1

# Kontrollera logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

### **"CI/CD pipeline failed"**
```bash
# Kontrollera GitHub Actions logs
# Gå till GitHub → Actions → Failed workflow → View logs

# Kontrollera secrets
# GitHub → Settings → Secrets and variables → Actions
```

---

## 🎉 **NÄSTA STEG EFTER DEPLOYMENT**

### **Omedelbart (idag):**
1. ✅ Verifiera att alla services är aktiva
2. ✅ Testa data collection pipeline
3. ✅ Verifiera att frontend/backend fungerar

### **Denna vecka:**
1. 🔄 Optimera AutoML model performance
2. 🔄 Implementera user authentication
3. 🔄 Lägg till fler monitoring alerts

### **Nästa vecka:**
1. 🚀 Implementera A/B testing
2. 🚀 Lägg till fler ML features
3. 🚀 Optimera kostnader baserat på usage

---

**🎯 När du har följt denna guide kommer du att ha en komplett, skalbar GCP production pipeline som automatiskt samlar data, tränar ML-modeller och serverar recommendations via en modern web-applikation!**
