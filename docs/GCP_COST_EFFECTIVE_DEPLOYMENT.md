# 🚀 GCP Kostnadseffektiv Deployment Guide

## ✅ **Status: Kursprojekt-fokuserad GCP Pipeline**

**Vår situation:**
- 🎓 **Kursprojekt** - 4 veckor kvar, behöver fungerande pipeline för betyg
- 💰 **$300 free credits** - Vill inte bränna i onödan
- 🎯 **100 spel** - Nuvarande dataset, vill expandera senare
- 📚 **Lärande-fokus** - Vill förstå varje steg, inte bygga production system

**Vad vi har implementerat:**
- ✅ **Secret Manager** - Säker lagring av IGDB credentials
- ✅ **Cloud Run (Data Collection)** - Serverless IGDB data collection med Docker
- ✅ **BigQuery** - Data warehouse för spel data (automatisk integration)
- ✅ **Google Container Registry** - Docker image storage
- 🔄 **Cloud Run (FastAPI + Next.js)** - Application hosting (nästa steg)
- 🔄 **Cloud Build CI/CD** - Automatisk deployment (nästa steg)
- 🔄 **Monitoring & Alerting** - Budget och performance alerts (nästa steg)
- 🔄 **Cloud Composer** - Planerat för senare (när vi har fungerande grund)

---

## 🎉 **AKTUELLA FRAMSTEG (2025-01-15) - PIPELINE KOMPLETT!**

### **✅ Vad vi har åstadkommit:**

**🔐 Secret Manager Setup:**
- ✅ Skapat `CLIENT_ID` och `CLIENT_SECRET` secrets
- ✅ Konfigurerat Cloud Run service account permissions
- ✅ Säker credential hantering för IGDB API

**🐳 Docker & Container Registry:**
- ✅ Byggt Docker image för IGDB data collection
- ✅ Pushat till Google Container Registry (`gcr.io/exalted-tempo-471613-e2/igdb-data-collector`)
- ✅ Konfigurerat Docker för GCR authentication

**☁️ Cloud Run Services (KOMPLETT PIPELINE):**
- ✅ **Data Collection:** `collect-igdb-data` service
  - Service URL: `https://collect-igdb-data-3sp2ul3fea-ew.a.run.app`
  - Testat med 20 spel - **FUNGERAR PERFEKT!**
- ✅ **Backend API:** `igdb-backend` service (BigQuery integration)
  - Service URL: `https://igdb-backend-3sp2ul3fea-ew.a.run.app`
  - Endpoints: `/games`, `/stats`, `/api/budget`, `/api/recommendations/*`
- ✅ **Frontend Dashboard:** `igdb-frontend` service
  - Service URL: `https://igdb-frontend-3sp2ul3fea-ew.a.run.app`
  - **FULLSTÄNDIGT FUNGERANDE DASHBOARD!** 🎉

**📊 BigQuery Integration:**
- ✅ Automatisk data upload till BigQuery
- ✅ Tabell: `exalted-tempo-471613-e2.igdb_game_data.games_raw`
- ✅ Data sparas som JSON med timestamp
- ✅ Backend läser direkt från BigQuery

**🔧 Problem-solving (ALLA LÖSTA):**
- ✅ Löst IGDB release_dates komplexitet (hoppar över för nu)
- ✅ Fixat Python scope issues med helper functions
- ✅ Hanterat Secret Manager permissions
- ✅ Fixat Docker build errors (`COPY data/` problem)
- ✅ Fixat Pydantic validation för `release_year` som kan vara `None`
- ✅ Fixat Frontend TypeScript errors i `pipeline-canvas.tsx`
- ✅ Fixat Frontend-Backend connection (localhost → Cloud Run URLs)
- ✅ Lade till saknade API endpoints för frontend kompatibilitet
- ✅ Fixat BigQuery response format och `DataQualityReport` struktur

### **🎉 PIPELINE STATUS: FULLSTÄNDIGT FUNGERANDE!**
- ✅ **End-to-End:** IGDB API → Cloud Storage → BigQuery → FastAPI → Next.js Dashboard
- ✅ **20 spel** visas korrekt i dashboard
- ✅ **Inga fel** i browser console
- ✅ **Alla endpoints** fungerar
- ✅ **Live data** från BigQuery till frontend

### **📈 Senaste Test Resultat:**
```json
{
  "status": "success",
  "games_collected": 20,
  "file_saved": "raw_data/igdb_games_20250115_121608.json",
  "bigquery_table": "exalted-tempo-471613-e2.igdb_game_data.games_raw",
  "timestamp": "20250115_121608"
}
```

---

## 🎯 **UPPDATERAD DEPLOYMENT ROADMAP**

### **Fas 1: Enkel Pipeline (1-2 dagar) - AKTUELL**

#### **1.1 Cloud Functions Setup (IGDB Data Collection)**

```bash
# Aktivera venv först
source venv/bin/activate

# Aktivera nödvändiga APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Skapa secrets för IGDB credentials
echo "your-twitch-client-id" | gcloud secrets create igdb-client-id --data-file=-
echo "your-twitch-client-secret" | gcloud secrets create igdb-client-secret --data-file=-

# Deploy Cloud Function för data collection
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

#### **1.2 BigQuery Setup (Data Storage)**

```bash
# Skapa dataset för IGDB data
bq mk --dataset --location=EU exalted-tempo-471613-e2:igdb_game_data

# Skapa tabell för raw data
bq mk --table \
  --schema="id:INTEGER,name:STRING,summary:STRING,rating:FLOAT,release_year:INTEGER,genres:STRING,platforms:STRING,themes:STRING,game_modes:STRING,player_perspectives:STRING,collected_at:TIMESTAMP" \
  exalted-tempo-471613-e2:igdb_game_data.games_raw
```

#### **1.3 Cloud Run Setup (Application Hosting)**

```bash
# Bygg och push backend image
docker build -f Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-backend:latest .
docker push gcr.io/exalted-tempo-471613-e2/igdb-backend:latest

# Deploy backend till Cloud Run
gcloud run deploy igdb-backend \
  --image gcr.io/exalted-tempo-471613-e2/igdb-backend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,PROJECT_ID=exalted-tempo-471613-e2"

# Bygg och push frontend image
docker build -f frontend/Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest ./frontend
docker push gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest

# Deploy frontend till Cloud Run
BACKEND_URL=$(gcloud run services describe igdb-backend --region=europe-west1 --format='value(status.url)')
gcloud run deploy igdb-frontend \
  --image gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"
```

### **Fas 2: Expansion (1-2 dagar)**

#### **2.1 Skala till fler spel**

```bash
# Testa med 1000 spel
curl -X POST "https://europe-west1-exalted-tempo-471613-e2.cloudfunctions.net/igdb-data-collector" \
  -H "Content-Type: application/json" \
  -d '{"games_limit": 1000}'

# Övervaka kostnader
gcloud billing budgets list
```

#### **2.2 Förbättra ML-modellen**

```bash
# Kör lokal ML-träning med fler spel
source venv/bin/activate
python src/models/game_recommender.py --games-limit 1000

# Testa modellen
python src/models/game_recommender.py --test-model
```

### **Fas 3: Avancerat (valfritt)**

#### **3.1 Cloud Composer (När vi har fungerande grund)**

```bash
# Skapa Composer environment
gcloud composer environments create igdb-data-pipeline \
  --location=europe-west1-a \
  --python-version=3 \
  --node-count=3 \
  --machine-type=n1-standard-2 \
  --disk-size=100 \
  --environment-size=medium

# Ladda upp DAGs
COMPOSER_BUCKET=$(gcloud composer environments describe igdb-data-pipeline --location=europe-west1-a --format='value(config.dagGcsPrefix)' | sed 's|/dags||')
gsutil cp airflow/dags/*.py gs://$COMPOSER_BUCKET/dags/
```

#### **3.2 Vertex AI AutoML**

```bash
# Kör AutoML setup
python src/automl_setup.py

# Detta kommer:
# 1. Ladda data från BigQuery
# 2. Förbereda för AutoML
# 3. Skapa dataset i Vertex AI
# 4. Starta träningsjobb
```

---

## 💰 **KOSTNADJÄMFÖRELSE**

### **Alternativ 1: Enkel Pipeline (Rekommenderat)**

| **Service** | **Kostnad/Månad** | **Användning** |
|-------------|-------------------|----------------|
| **Cloud Functions** | ~$5 | Per anrop |
| **BigQuery** | ~$10 | Per query |
| **Cloud Run** | ~$15 | Per request |
| **Cloud Storage** | ~$5 | Per GB |
| **Total** | **~$35/månad** | **Skalbar** |

### **Alternativ 2: Cloud Composer Pipeline**

| **Service** | **Kostnad/Månad** | **Användning** |
|-------------|-------------------|----------------|
| **Cloud Composer** | ~$300 | 24/7 |
| **BigQuery** | ~$10 | Per query |
| **Cloud Run** | ~$15 | Per request |
| **Cloud Storage** | ~$5 | Per GB |
| **Total** | **~$330/månad** | **Fast kostnad** |

---

## 🎯 **VARFÖR ALTERNATIV 1?**

### **Fördelar:**
- ✅ **Kostnadseffektivt** - Sparar dina free credits
- ✅ **Snabbt att få igång** - Fungerande pipeline på några timmar
- ✅ **Lärande-värde** - Du lär dig Cloud Functions, BigQuery, Cloud Run
- ✅ **Skalbar** - Fungerar för 100 spel och 334,000 spel
- ✅ **Fokuserat** - Nå ditt mål snabbt

### **Nackdelar:**
- ❌ **Mindre orchestration** - Ingen Airflow DAG
- ❌ **Manuell skalning** - Måste hantera triggers själv
- ❌ **Mindre professionell** - Inte som verkliga production systems

---

## 🚀 **IMPLEMENTATION STEG**

### **Steg 1: Grundläggande Setup**

```bash
# Aktivera venv först
source venv/bin/activate

# Aktivera alla nödvändiga APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable monitoring.googleapis.com

# Verifiera att APIs är aktiverade
gcloud services list --enabled --filter="name:(cloudfunctions OR bigquery OR storage OR secretmanager OR run OR cloudbuild OR monitoring)"
```

### **Steg 2: Data Collection**

```bash
# Skapa secrets för IGDB credentials
echo "your-twitch-client-id" | gcloud secrets create igdb-client-id --data-file=-
echo "your-twitch-client-secret" | gcloud secrets create igdb-client-secret --data-file=-

# Deploy Cloud Function
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

### **Steg 3: Data Storage**

```bash
# Skapa BigQuery dataset
bq mk --dataset --location=EU exalted-tempo-471613-e2:igdb_game_data

# Skapa tabell för raw data
bq mk --table \
  --schema="id:INTEGER,name:STRING,summary:STRING,rating:FLOAT,release_year:INTEGER,genres:STRING,platforms:STRING,themes:STRING,game_modes:STRING,player_perspectives:STRING,collected_at:TIMESTAMP" \
  exalted-tempo-471613-e2:igdb_game_data.games_raw
```

### **Steg 4: Application Deployment**

```bash
# Deploy backend
docker build -f Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-backend:latest .
docker push gcr.io/exalted-tempo-471613-e2/igdb-backend:latest

gcloud run deploy igdb-backend \
  --image gcr.io/exalted-tempo-471613-e2/igdb-backend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10

# Deploy frontend
docker build -f frontend/Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest ./frontend
docker push gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest

BACKEND_URL=$(gcloud run services describe igdb-backend --region=europe-west1 --format='value(status.url)')
gcloud run deploy igdb-frontend \
  --image gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"
```

---

## 📊 **MONITORING OCH KOSTNADSHANTERING**

### **Budget Alerts**

```bash
# Skapa budget alert
gcloud billing budgets create \
  --billing-account=$(gcloud billing accounts list --format='value(name)' | head -1) \
  --display-name="IGDB Pipeline Budget Alert" \
  --budget-amount=100USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100 \
  --notification-rule=email=johanenstam@gmail.com
```

### **Kostnadsövervakning**

```bash
# Kontrollera dagliga kostnader
gcloud billing budgets list

# Kontrollera service-specifika kostnader
gcloud logging read "resource.type=cloud_function" --limit=10
gcloud logging read "resource.type=cloud_run_revision" --limit=10
```

---

## 🎓 **LÄRANDE-MÅL**

### **Vad du kommer lära dig:**

1. **Cloud Functions** - Serverless computing
2. **BigQuery** - Data warehouse och SQL
3. **Cloud Run** - Container hosting
4. **Secret Manager** - Säker credential hantering
5. **Cloud Build** - CI/CD pipelines
6. **Monitoring** - Kostnad och performance tracking

### **Nästa steg - SERVERLESS ML PIPELINE:**

1. **ML Training Function** - Automatisk model training (Cloud Functions)
2. **Model Serving Function** - Live rekommendationer (Cloud Functions)
3. **Cloud Scheduler** - Automatisk orchestration (Serverless)
4. **Backend Integration** - ML model i FastAPI
5. **Frontend Recommendations** - Rekommendationsfunktionalitet
6. **Skala till fler spel** - 1000+ spel från IGDB

**📋 Detaljerad plan:** Se `docs/SERVERLESS_ML_PIPELINE.md`

**💰 Kostnad:** ~$15-30/månad (vs $300-400/månad för Cloud Composer)

---

## 🚨 **TROUBLESHOOTING**

### **Vanliga problem:**

**"Cloud Function timeout"**
```bash
# Öka timeout
gcloud functions deploy igdb-data-collector --timeout 900s
```

**"BigQuery permission denied"**
```bash
# Kontrollera service account permissions
gcloud projects get-iam-policy exalted-tempo-471613-e2
```

**"Cloud Run deployment failed"**
```bash
# Kontrollera Docker build
docker build -f Dockerfile -t test-backend .
docker run -p 8000:8000 test-backend
```

---

## 🎉 **NÄSTA STEG**

### **Omedelbart (idag):**
1. ✅ Aktivera alla nödvändiga APIs
2. ✅ Skapa secrets för IGDB credentials
3. ✅ Deploya Cloud Run service för data collection
4. ✅ Testa IGDB data collection (5 spel samlade!)

### **Denna vecka:**
1. 🔄 Sätt upp BigQuery dataset
2. 🔄 Deploya Cloud Run services
3. 🔄 Testa hela pipeline med 100 spel

### **Nästa vecka:**
1. 🚀 Skala till fler spel (1000+)
2. 🚀 Förbättra ML-modellen
3. 🚀 Lägg till Cloud Composer (valfritt)

---

**🎯 När du har följt denna guide kommer du att ha en kostnadseffektiv, skalbar GCP pipeline som fungerar för ditt kursprojekt och kan expanderas när du är redo!**
