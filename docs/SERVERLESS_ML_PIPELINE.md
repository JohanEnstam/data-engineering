# 🚀 Serverless ML Pipeline - Implementation Plan

## 🎯 **Översikt**

Denna guide dokumenterar vår serverless ML pipeline implementation med fokus på kostnadseffektivitet och snabb utveckling. Vi använder Cloud Functions + Cloud Scheduler istället för Cloud Composer för att undvika onödig komplexitet och höga kostnader.

---

## 🏗️ **Arkitektur - FABRIKEN vs 🏪 BUTIKEN**

### **🏭 FABRIKEN (Data Pipeline + ML Training)**
```
IGDB API → Cloud Storage → BigQuery → ML Training → Model Storage
    ↓           ↓            ↓           ↓            ↓
Cloud Functions + Cloud Scheduler (Serverless Orchestration)
```

### **🏪 BUTIKEN (Application Layer)**
```
FastAPI Backend → Model Loading → Recommendations → Next.js Frontend
```

---

## 📊 **Kostnadsanalys**

### **Serverless vs Cloud Composer**
| Komponent | Serverless | Cloud Composer | Besparing |
|-----------|------------|----------------|-----------|
| **Base Cost** | $15/månad | $300/månad | $285/månad |
| **100 spel** | $20/månad | $350/månad | $330/månad |
| **1000+ spel** | $30/månad | $400/månad | $370/månad |
| **Maintenance** | Zero | High | Time saved |

**💰 Total besparing: $300-370/månad**

---

## 🚀 **IMPLEMENTATIONSPLAN**

### **FAS 1: ML Training Pipeline (1-2 dagar)**

#### **1.1 ML Training Cloud Function**
```python
# gcp/ml_training_function.py
def train_recommendation_model(request):
    """
    Cloud Function för ML model training
    - Läser data från BigQuery
    - Tränar rekommendationsmodell
    - Sparar model till Cloud Storage
    - Returnerar training metrics
    """
```

**Teknisk implementation:**
- **Trigger:** HTTP (kallas från Cloud Scheduler)
- **Runtime:** Python 3.9
- **Memory:** 2GB (för ML training)
- **Timeout:** 9 minuter (max för Cloud Functions)
- **Dependencies:** scikit-learn, pandas, numpy, google-cloud-bigquery

#### **1.2 Model Storage Strategy**
```bash
# Cloud Storage bucket structure
gs://igdb-ml-models/
├── models/
│   ├── game_recommender_v1.pkl
│   ├── game_recommender_v2.pkl
│   └── latest_model.pkl
├── metadata/
│   ├── training_metrics.json
│   └── model_versions.json
└── backups/
    └── archived_models/
```

#### **1.3 Training Data Pipeline**
```python
# Data flow för ML training
BigQuery → Feature Engineering → Model Training → Model Validation → Model Storage
```

**Features för rekommendationsmodell:**
- **Game Genres:** One-hot encoding av genres
- **Platforms:** One-hot encoding av platforms  
- **Themes:** One-hot encoding av themes
- **Rating:** Normalized rating scores
- **Release Year:** Normalized release years
- **Popularity:** IGDB popularity scores

### **FAS 2: Model Serving Pipeline (1 dag)**

#### **2.1 Model Serving Cloud Function**
```python
# gcp/model_serving_function.py
def get_recommendations(request):
    """
    Cloud Function för model serving
    - Laddar senaste model från Cloud Storage
    - Tar game_id som input
    - Returnerar top 10 rekommendationer
    """
```

**API Endpoints:**
- `POST /recommendations` - Get recommendations for a game
- `GET /recommendations/{game_id}` - Get recommendations by game ID
- `GET /model/status` - Check model status and version

#### **2.2 Model Loading Strategy**
```python
# Efficient model loading
- Cache model i memory (Cloud Function instance reuse)
- Lazy loading (load on first request)
- Version management (rollback capability)
- Health checks (model validation)
```

### **FAS 3: Orchestration Setup (1 dag)**

#### **3.1 Cloud Scheduler Configuration**
```bash
# Daglig ML training pipeline
gcloud scheduler jobs create http ml-training-pipeline \
  --schedule="0 2 * * *" \
  --uri="https://europe-west1-exalted-tempo-471613-e2.cloudfunctions.net/train-recommendation-model" \
  --http-method=POST \
  --time-zone="Europe/Stockholm"
```

**Scheduler Jobs:**
1. **Daily Training:** 02:00 UTC (daglig model training)
2. **Data Collection:** 01:00 UTC (IGDB data collection)
3. **Model Validation:** 03:00 UTC (model performance check)

#### **3.2 Pipeline Dependencies**
```python
# Orchestration flow
1. Data Collection (01:00) → BigQuery
2. ML Training (02:00) → Model Storage  
3. Model Validation (03:00) → Health Check
4. Model Serving (On-demand) → Recommendations
```

### **FAS 4: Backend Integration (1 dag)**

#### **4.1 FastAPI Backend Updates**
```python
# src/api_endpoints/main_bigquery.py
# Lägg till ML integration endpoints

@app.post("/api/recommendations/search")
async def search_recommendations(query: str):
    """
    Search for games and return recommendations
    """
    
@app.get("/api/recommendations/{game_id}")
async def get_game_recommendations(game_id: int):
    """
    Get recommendations for specific game
    """
```

#### **4.2 Model Integration**
```python
# src/models/ml_integration.py
class MLModelManager:
    """
    Hanterar ML model loading och serving
    - Laddar model från Cloud Storage
    - Cachar model i memory
    - Hanterar model versions
    """
```

### **FAS 5: Frontend Integration (1 dag)**

#### **5.1 Recommendation Components**
```typescript
// frontend/src/components/recommendations/
├── RecommendationCard.tsx
├── RecommendationList.tsx
├── GameSearchWithRecommendations.tsx
└── RecommendationEngine.tsx
```

#### **5.2 API Integration**
```typescript
// frontend/src/lib/recommendations.ts
export class RecommendationAPI {
  async getRecommendations(gameId: number): Promise<Game[]>
  async searchWithRecommendations(query: string): Promise<SearchResult[]>
  async getSimilarGames(gameId: number): Promise<Game[]>
}
```

---

## 🔧 **TEKNISK IMPLEMENTATION**

### **Cloud Functions Setup**
```bash
# 1. ML Training Function
gcloud functions deploy train-recommendation-model \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 2048MB \
  --timeout 540s \
  --region europe-west1 \
  --source gcp/ml_training_function.py

# 2. Model Serving Function  
gcloud functions deploy get-recommendations \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 1024MB \
  --timeout 60s \
  --region europe-west1 \
  --source gcp/model_serving_function.py
```

### **Cloud Storage Setup**
```bash
# Skapa ML models bucket
gsutil mb gs://igdb-ml-models-eu-$(date +%s)

# Set permissions
gsutil iam ch allUsers:objectViewer gs://igdb-ml-models-eu-*
```

### **Cloud Scheduler Setup**
```bash
# Aktivera Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# Skapa scheduler jobs
gcloud scheduler jobs create http ml-training-pipeline \
  --schedule="0 2 * * *" \
  --uri="https://europe-west1-exalted-tempo-471613-e2.cloudfunctions.net/train-recommendation-model" \
  --http-method=POST \
  --time-zone="Europe/Stockholm"
```

---

## 📈 **SCALING STRATEGY**

### **Fas 1: 100 spel (Nu)**
- **Training Time:** ~2-3 minuter
- **Model Size:** ~1-2MB
- **Cost:** ~$15/månad
- **Complexity:** Låg

### **Fas 2: 1000+ spel (Om 2-3 veckor)**
- **Training Time:** ~5-7 minuter
- **Model Size:** ~5-10MB
- **Cost:** ~$30/månad
- **Complexity:** Medium

### **Fas 3: 10000+ spel (Om 1-2 månader)**
- **Migration:** Cloud Composer eller Custom Airflow
- **Training Time:** ~15-20 minuter
- **Model Size:** ~20-50MB
- **Cost:** ~$100-300/månad
- **Complexity:** Hög

---

## 🎯 **SUCCESS METRICS**

### **Tekniska Metrics**
- ✅ **Training Success Rate:** >95%
- ✅ **Model Accuracy:** >80% (baserat på test data)
- ✅ **Response Time:** <2 sekunder för rekommendationer
- ✅ **Uptime:** >99% för serving functions

### **Business Metrics**
- ✅ **User Engagement:** Antal rekommendationer som klickas
- ✅ **Model Performance:** Hur bra rekommendationer är
- ✅ **Cost Efficiency:** Kostnad per rekommendation
- ✅ **Scalability:** Hur snabbt vi kan hantera fler spel

---

## 🚨 **RISK MANAGEMENT**

### **Tekniska Risker**
- **Cloud Function Timeout:** Max 9 minuter (hanteras med chunking)
- **Memory Limits:** Max 8GB (hanteras med model optimization)
- **Cold Starts:** ~2-3 sekunder (hanteras med warming)

### **Business Risker**
- **Model Accuracy:** Kontinuerlig monitoring och validation
- **Cost Overrun:** Budget alerts och monitoring
- **Data Quality:** Validation och error handling

---

## 📚 **LEARNING OUTCOMES**

### **Tekniska Färdigheter**
- ✅ **Cloud Functions:** Serverless computing
- ✅ **ML Pipeline:** End-to-end machine learning
- ✅ **Model Serving:** Production ML deployment
- ✅ **Cloud Scheduler:** Automated orchestration
- ✅ **Cost Optimization:** Budget-conscious cloud architecture

### **Business Färdigheter**
- ✅ **ML Product Development:** Från data till produkt
- ✅ **Scalability Planning:** Growth strategy
- ✅ **Cost Management:** Budget optimization
- ✅ **Performance Monitoring:** ML model monitoring

---

## 🎉 **EXPECTED OUTCOMES**

### **Efter Fas 1-5 (1 vecka):**
- ✅ **Fungerande ML Pipeline:** Automatisk training och serving
- ✅ **Recommendation Engine:** Live rekommendationer i frontend
- ✅ **Cost Effective:** <$30/månad total kostnad
- ✅ **Scalable Foundation:** Redo för 1000+ spel

### **Efter Scaling (2-3 veckor):**
- ✅ **Production Ready:** Robust ML pipeline
- ✅ **High Performance:** Snabba rekommendationer
- ✅ **Cost Optimized:** Optimal kostnad per rekommendation
- ✅ **Learning Complete:** Full ML pipeline mastery

---

## 🔄 **CI/CD INTEGRATION STRATEGY**

### **🎯 Enklaste och Bästa Alternativen:**

#### **1. �� Cloud Functions Deployment**
**Val:** Integrera ML functions i befintlig CI/CD
```yaml
# Lägg till i .github/workflows/gcp-deployment.yml
- name: Deploy ML Functions
  if: github.ref == 'refs/heads/develop'  # Bara staging först
  run: |
    # Deploy ML training function
    gcloud functions deploy train-recommendation-model \
      --source gcp/ml_training_function.py \
      --runtime python39 \
      --trigger-http \
      --memory 2048MB \
      --timeout 540s \
      --region europe-west1
    
    # Deploy model serving function
    gcloud functions deploy get-recommendations \
      --source gcp/model_serving_function.py \
      --runtime python39 \
      --trigger-http \
      --memory 1024MB \
      --timeout 60s \
      --region europe-west1
```

#### **2. 📦 Model Storage Strategy**
**Val:** Enkel Cloud Storage versioning
```bash
# Model storage structure
gs://igdb-ml-models-eu-$(date +%s)/
├── latest/
│   ├── game_recommender.pkl
│   └── metadata.json
├── v1.0.0/
│   ├── game_recommender.pkl
│   └── metadata.json
└── backups/
    └── archived_models/
```

#### **3. 🧪 Testing Strategy**
**Val:** Lägg till ML tests i befintlig test suite
```python
# tests/test_ml_functions.py
def test_train_recommendation_model():
    """Test ML training function"""
    # Mock BigQuery data
    # Test model training
    # Validate model output

def test_get_recommendations():
    """Test model serving function"""
    # Mock model loading
    # Test recommendations
    # Validate response format
```

#### **4. 📊 Monitoring Strategy**
**Val:** Integrera ML monitoring i befintlig setup
```yaml
# Lägg till i gcp-deployment.yml
- name: Setup ML Monitoring
  run: |
    # Cloud Monitoring för ML functions
    gcloud monitoring uptime-checks create \
      --display-name="ML Training Function" \
      --http-check-path="/health" \
      --region europe-west1
```

#### **5. 🔐 Secrets Management**
**Val:** Använd befintlig `GCP_SA_KEY` secret
```bash
# Lägg till ML-specifika permissions
gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
    --member="serviceAccount:github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com" \
    --role="roles/storage.admin"  # För model storage

gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
    --member="serviceAccount:github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"  # För ML training data
```

### **📋 CI/CD Workflow Updates:**

#### **Befintlig Workflow: `.github/workflows/gcp-deployment.yml`**
```yaml
# Lägg till ML deployment efter Cloud Run deployment
- name: Deploy ML Functions
  needs: test-and-quality
  if: github.ref == 'refs/heads/develop'
  run: |
    # Deploy ML functions
    # Test ML pipeline
    # Validate model storage
```

#### **Befintlig Workflow: `.github/workflows/simple-ci.yml`**
```yaml
# Lägg till ML tests efter Python tests
- name: Run ML Function Tests
  run: |
    # Test ML training function
    # Test model serving function
    # Validate ML pipeline
```

---

## 🔄 **NEXT STEPS - UPPDATERAD MED CI/CD INTEGRATION**

### **FAS 1: ML Functions + CI/CD Integration (1-2 dagar)**

1. **Implementera ML Training Function** (Idag)
2. **Sätt upp Model Storage** (Idag)
3. **Skapa Model Serving Function** (Idag)
4. **Integrera ML functions i befintlig CI/CD** (Idag)
5. **Lägg till ML tests i befintlig test suite** (Idag)

### **FAS 2: Orchestration + Backend Integration (1 dag)**

6. **Konfigurera Cloud Scheduler** (Imorgon)
7. **Integrera ML model i FastAPI Backend** (Imorgon)
8. **Uppdatera Frontend med rekommendationer** (Imorgon)

### **FAS 3: Testing + Monitoring (1 dag)**

9. **Testa hela ML pipeline** (Imorgon)
10. **Lägg till ML monitoring** (Imorgon)
11. **Skala till fler spel** (Nästa vecka)

**🎯 Mål:** Fungerande ML pipeline med CI/CD integration inom 1 vecka!
