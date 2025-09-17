# 🚀 GCP Implementation Roadmap - Uppdaterad med CI/CD Integration

## 🎯 **Översikt**

Denna roadmap sammanställer vår fortsatta GCP implementation med fokus på enkel CI/CD integration och serverless ML pipeline. Vi använder befintlig CI/CD setup och lägger till ML funktionalitet på det enklaste sättet.

---

## 📊 **AKTUELL STATUS**

### **✅ Vad vi har (Fungerande):**
- **Cloud Run Services:** Data collection, Backend API, Frontend Dashboard
- **BigQuery Integration:** Live data från IGDB API
- **CI/CD Pipeline:** GitHub Actions med staging/production deployment
- **Docker Registry:** GCR integration med automatisk builds
- **Secret Management:** Twitch credentials säkert lagrade

### **🔄 Vad vi ska bygga (Nästa steg):**
- **ML Training Function:** Automatisk model training
- **Model Serving Function:** Live rekommendationer
- **Cloud Scheduler:** Automatisk orchestration
- **ML Integration:** Backend + Frontend rekommendationer

---

## 🏗️ **ARKITEKTUR - FABRIKEN vs 🏪 BUTIKEN**

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

### **🔄 CI/CD Integration**
```
GitHub Actions → Docker Builds → GCR → Cloud Run + Cloud Functions
```

---

## 🚀 **IMPLEMENTATIONSPLAN**

### **FAS 1: ML Functions + CI/CD Integration (1-2 dagar)**

#### **1.1 ML Training Function**
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

#### **1.2 Model Serving Function**
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

#### **1.3 Model Storage Setup**
```bash
# Cloud Storage bucket structure
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

#### **1.4 CI/CD Integration**
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

#### **1.5 ML Testing**
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

### **FAS 2: Orchestration + Backend Integration (1 dag)**

#### **2.1 Cloud Scheduler Setup**
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

#### **2.2 Backend ML Integration**
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

#### **2.3 Frontend Recommendations**
```typescript
// frontend/src/components/recommendations/
├── RecommendationCard.tsx
├── RecommendationList.tsx
├── GameSearchWithRecommendations.tsx
└── RecommendationEngine.tsx
```

### **FAS 3: Testing + Monitoring (1 dag)**

#### **3.1 End-to-End Testing**
```python
# tests/test_ml_integration.py
def test_end_to_end_ml_pipeline():
    """
    Test hela ML pipeline
    - Data collection → training → serving
    - Validate recommendations quality
    """
```

#### **3.2 ML Monitoring**
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

---

## 💰 **KOSTNADSANALYS**

### **Serverless vs Cloud Composer**
| Komponent | Serverless | Cloud Composer | Besparing |
|-----------|------------|----------------|-----------|
| **Base Cost** | $15/månad | $300/månad | $285/månad |
| **100 spel** | $20/månad | $350/månad | $330/månad |
| **1000+ spel** | $30/månad | $400/månad | $370/månad |
| **Maintenance** | Zero | High | Time saved |

**💰 Total besparing: $300-370/månad med serverless!**

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

### **CI/CD Permissions**
```bash
# Lägg till ML-specifika permissions
gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
    --member="serviceAccount:github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com" \
    --role="roles/storage.admin"  # För model storage

gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
    --member="serviceAccount:github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"  # För ML training data
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
- ✅ **CI/CD Integration:** Automated ML deployment

### **Business Färdigheter**
- ✅ **ML Product Development:** Från data till produkt
- ✅ **Scalability Planning:** Growth strategy
- ✅ **Cost Management:** Budget optimization
- ✅ **Performance Monitoring:** ML model monitoring

---

## 🎉 **EXPECTED OUTCOMES**

### **Efter Fas 1-3 (1 vecka):**
- ✅ **Fungerande ML Pipeline:** Automatisk training och serving
- ✅ **Recommendation Engine:** Live rekommendationer i frontend
- ✅ **Cost Effective:** <$30/månad total kostnad
- ✅ **CI/CD Integrated:** Automatisk ML deployment
- ✅ **Scalable Foundation:** Redo för 1000+ spel

### **Efter Scaling (2-3 veckor):**
- ✅ **Production Ready:** Robust ML pipeline
- ✅ **High Performance:** Snabba rekommendationer
- ✅ **Cost Optimized:** Optimal kostnad per rekommendation
- ✅ **Learning Complete:** Full ML pipeline mastery

---

## 🔄 **NEXT STEPS**

1. **Implementera ML Training Function** (Idag)
2. **Sätt upp Model Storage** (Idag)
3. **Skapa Model Serving Function** (Idag)
4. **Integrera ML functions i befintlig CI/CD** (Idag)
5. **Lägg till ML tests i befintlig test suite** (Idag)
6. **Konfigurera Cloud Scheduler** (Imorgon)
7. **Integrera ML model i FastAPI Backend** (Imorgon)
8. **Uppdatera Frontend med rekommendationer** (Imorgon)
9. **Testa hela ML pipeline** (Imorgon)
10. **Lägg till ML monitoring** (Imorgon)
11. **Skala till fler spel** (Nästa vecka)

**🎯 Mål:** Fungerande ML pipeline med CI/CD integration inom 1 vecka, redo för scaling inom 2-3 veckor!
