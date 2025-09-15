# IGDB Spelrekommendationssystem - Utvecklingsguide

## 🎯 **Projektmål**

**Huvudmål:** Bygga ett komplett spelrekommendationssystem med IGDB API som datakälla, implementerat som en fullständig data pipeline i Google Cloud Platform.

**Slutprodukt:** En webbapplikation där användare kan skriva in spel-titlar och få rekommendationer på liknande spel baserat på ML-algoritmer.

---

## 🏗️ **Teknisk Arkitektur**

### **Data Pipeline (End-to-End)**
```
IGDB API → Airflow → Cloud Storage → BigQuery → dbt → ML Processing → FastAPI → Next.js Frontend
```

**Airflow Orchestration:**
- **Data Collection:** IGDB API → Local JSON files
- **Storage Upload:** Local files → Google Cloud Storage
- **BigQuery Load:** GCS → BigQuery raw tables
- **dbt Transformations:** Raw data → ML-ready features
- **ML Training:** Transformed data → Trained models

### **Teknisk Stack**
- **Backend:** Python, FastAPI, IGDB API
- **Data Processing:** BigQuery, dbt (data build tool)
- **Data Orchestration:** Apache Airflow 3.0 ⭐ **IMPLEMENTERAT**
- **ML:** scikit-learn, pandas, numpy
- **Storage:** Google Cloud Storage ⭐ **IMPLEMENTERAT**
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Cloud:** Google Cloud Platform (GCP) ⭐ **CLOUD RUN DEPLOYED**
- **CI/CD:** GitHub Actions
- **Containerization:** Docker ⭐ **GCR INTEGRATION**
- **Secrets:** Google Secret Manager ⭐ **IMPLEMENTERAT**

---

## 🚀 **GCP DEPLOYMENT STATUS (2025-01-15)**

### **✅ Implementerat i molnet - PIPELINE KOMPLETT!**

**🔐 Secret Manager:**
- ✅ IGDB API credentials säkert lagrade
- ✅ Cloud Run service account permissions konfigurerade

**🐳 Docker & Container Registry:**
- ✅ Alla services containerized (data collection, backend, frontend)
- ✅ Images pushade till Google Container Registry
- ✅ Docker authentication konfigurerad

**☁️ Cloud Run Services (KOMPLETT PIPELINE):**
- ✅ **Data Collection:** `collect-igdb-data` service
  - URL: `https://collect-igdb-data-3sp2ul3fea-ew.a.run.app`
  - **TESTAT: 20 spel samlade från IGDB API**
- ✅ **Backend API:** `igdb-backend` service (BigQuery integration)
  - URL: `https://igdb-backend-3sp2ul3fea-ew.a.run.app`
  - Endpoints: `/games`, `/stats`, `/api/budget`, `/api/recommendations/*`
- ✅ **Frontend Dashboard:** `igdb-frontend` service
  - URL: `https://igdb-frontend-3sp2ul3fea-ew.a.run.app`
  - **FULLSTÄNDIGT FUNGERANDE DASHBOARD!** 🎉

**📊 BigQuery Integration:**
- ✅ Automatisk data upload från Cloud Run
- ✅ Tabell: `exalted-tempo-471613-e2.igdb_game_data.games_raw`
- ✅ JSON format med timestamps
- ✅ Backend läser direkt från BigQuery
- ✅ Frontend visar live data från BigQuery

### **🎉 PIPELINE STATUS: FULLSTÄNDIGT FUNGERANDE!**
- ✅ **End-to-End:** IGDB API → Cloud Storage → BigQuery → FastAPI → Next.js Dashboard
- ✅ **20 spel** visas korrekt i dashboard
- ✅ **Inga fel** i browser console
- ✅ **Alla endpoints** fungerar
- ✅ **Live data** från BigQuery till frontend

### **🔄 Nästa steg (valfritt):**
1. **Skala till fler spel** - 1000+ spel från IGDB
2. **Cloud Composer** - Automatisk scheduling (valfritt)
3. **ML Pipeline** - Rekommendationsmodell (valfritt)

---

## 📊 **Data Källa: IGDB API**

### **Tillgänglig Data (15+ Datatyper)**
- **Spel (Games):** namn, beskrivning, storyline, betyg, releasedatum, genrer, plattformar, teman
- **Kategorisering:** genrer, plattformar, teman, spelmoder, perspektiv
- **Företag:** utvecklare, utgivare, beskrivningar, länder
- **Media:** covers, screenshots, videos, websites
- **Tidsdata:** release dates, timestamps

### **Data Volym & Kvalitet**
- **~500,000+ spel** i databasen
- **~50+ genrer** och **~100+ teman**
- **~200+ plattformar** (alla tider)
- **~10,000+ företag** (utvecklare/utgivare)
- **Miljontals bilder** (covers, screenshots)
- **Hög datakvalitet:** Strukturerad, verifierad, historisk data

### **API Begränsningar**
- **Rate limit:** ~30 requests per minute
- **Gratis tier:** Bra för testning och små projekt
- **Autentisering:** OAuth2 via Twitch Developer Portal

---

## 🤖 **Machine Learning Approach**

### **Rekommendationssystem (Huvudfokus)**
**Mål:** Rekommendera liknande spel baserat på användarinput

**Algoritmer:**
1. **Content-Based Filtering**
   - Analysera spel-genres, teman, plattformar
   - Beräkna similarity scores
   - Rekommendera spel med liknande attribut

2. **Collaborative Filtering** (om användardata finns)
   - "Användare som gillade X gillade också Y"
   - Använda rating-data för rekommendationer

3. **Hybrid Approach**
   - Kombinera content-based och collaborative
   - Viktning baserat på tillgänglig data

### **Feature Engineering**
```python
# Spel-attribut för ML:
- Genres (one-hot encoding)
- Themes (one-hot encoding)
- Platforms (one-hot encoding)
- Game modes (one-hot encoding)
- Player perspectives (one-hot encoding)
- Release year (numerical)
- Rating scores (numerical)
- Text features (TF-IDF på summaries)
```

---

## 🎨 **Användarupplevelse**

### **Frontend (Next.js + shadcn/ui)**
**Huvudfunktioner:**
- **Sökfält:** Användare skriver in spel-titlar
- **Rekommendationer:** Visar liknande spel med:
  - Spel-titel och beskrivning
  - Cover-bild
  - Genres och teman
  - Rating och releasedatum
  - Likhetsscore
- **Filtrering:** Filtrera på genre, plattform, år
- **Responsiv design:** Fungerar på desktop och mobil

### **API Endpoints (FastAPI)**
```python
# Huvudendpoints:
GET /api/games/search?query={game_name}
GET /api/games/recommendations?game_id={id}&limit={n}
GET /api/games/{id}
GET /api/genres
GET /api/platforms
POST /api/recommendations/batch  # För flera spel samtidigt
```

### **Frontend Development & Empty State Handling** ⭐ **IMPLEMENTERAT** ✅

**Problem som löstes:**
- Mock-data var förvirrande och visade inte verklig data
- API kunde inte ladda NDJSON-format korrekt
- Ingen tydlig feedback när data saknades

**Lösningar implementerade:**
- **API Data Loading:** Stöd för NDJSON-format och automatisk data type conversion
- **Empty State Management:** Proper loading, error och empty states med retry funktionalitet
- **Mock Data Removal:** Borttaget all mock-data och ersatt med riktig IGDB API data
- **User Experience:** Tydliga meddelanden och retry-knappar för bättre användarupplevelse

**Resultat:**
- ✅ Riktig data från IGDB API (100 games)
- ✅ Tydliga meddelanden när data saknas eller fel uppstår
- ✅ Clean code utan förvirrande mock-data logik

---

## 🚀 **Utvecklingsfaser**

### **Fas 1: Frontend-First Prototyping** ⭐ **KLAR** ✅
**Mål:** Visuell feedback och iterativ utveckling

**Uppgifter:**
- [x] Skapa projektstruktur enligt best practice
- [x] Migrera Isaks IGDB API kod till `src/api/`
- [x] Utveckla data collection script
- [x] Bygg data preprocessing pipeline
- [x] **Frontend setup** med Next.js + shadcn/ui
- [x] **Data visualization** - visa testdata i tables/charts
- [x] **Budget tracking** dashboard för GCP credits
- [x] **Basic API endpoints** för data access
- [x] **GCP Integration** - budget monitoring med verklig data
- [x] **Empty State Handling** - proper error handling och user feedback
- [x] **API Data Loading** - NDJSON support och data type conversion

### **Fas 2: Local-First ML Development** ⭐ **KLAR** ✅
**Mål:** Bygga robust rekommendationsmotor lokalt innan cloud scaling

**Strategi:** "Progressive Local-First" - utveckla och testa allt lokalt först

**Uppgifter:**
- [x] **Data Collection (1,000+ spel)** - samla tillräckligt med data lokalt
- [x] **Progressive feature engineering** - börja med core features (genres, themes)
- [x] **Local model training** på MacBook med scikit-learn
- [x] **Manual evaluation system** - "Ser dessa rekommendationer rimliga ut?"
- [x] **Frontend integration** - sök + rekommendationer i UI
- [x] **Model comparison** - testa olika algoritmer visuellt
- [x] **Performance optimization** för lokala constraints
- [x] **Data quality validation** med visuell feedback

### **Fas 3: Docker & CI/CD Integration** ⭐ **KLAR** ✅
**Mål:** Containerisering och CI/CD-pipeline för skalning till molnet

**Uppgifter:**
- [x] **GCP budget tracking** - real-time cost monitoring
- [x] **Docker containerization** - Frontend + Backend + PostgreSQL
- [x] **TypeScript/ESLint fixes** - Clean builds utan fel
- [x] **Lokal Docker-testning** - Alla services fungerar perfekt
- [x] **GitHub Actions CI/CD** - Simple CI pipeline implementerad och fungerar
- [x] **GitHub CLI Integration** - Direkt workflow-övervakning från terminal
- [x] **Python Code Quality** - Black, flake8, isort automation
- [x] **Pre-commit Hooks** - Lokal kodkvalitet före commit
- [x] **Status Badges** - Real-time CI/CD status i README
- [x] **Frontend Component Fixes** - TypeScript path mapping fixade, Docker build fungerar

### **Fas 4: Airflow Data Pipeline** ⭐ **KLAR** ✅
**Mål:** Automatiserad data pipeline från IGDB API till ML-modeller

**Uppgifter:**
- [x] **Airflow 3.0 Installation** - Apache Airflow med Google providers
- [x] **Cloud Storage Setup** - GCS buckets för raw och processed data
- [x] **Airflow DAG Development** - Komplett pipeline DAG implementerad
- [x] **Data Collection Task** - IGDB API → Local JSON files
- [x] **Storage Upload Task** - Local files → Google Cloud Storage
- [x] **BigQuery Load Task** - GCS → BigQuery raw tables
- [x] **dbt Integration Task** - Raw data → ML-ready features
- [x] **ML Training Task** - Transformed data → Trained models
- [x] **Test DAG** - Verifiering av alla komponenter
- [x] **GCP Authentication** - Service account integration
- [x] **Airflow Configuration** - JWT secrets och säkra nycklar
- [x] **Web UI Access** - http://localhost:8080 fungerar perfekt
- [x] **Documentation** - Komplett setup guide i docs/AIRFLOW_SETUP.md

### **Fas 4: Airflow Data Pipeline** ⭐ **KLAR** ✅
**Mål:** Automatiserad data pipeline från IGDB API till ML-modeller

**Implementation:**
- **Airflow 3.0** - Apache Airflow med Google providers
- **Cloud Storage** - GCS buckets för raw och processed data
- **DAG Development** - Komplett pipeline med 5 tasks
- **GCP Integration** - Service account authentication
- **Web UI** - http://localhost:8080 för monitoring
- **Documentation** - Komplett setup guide i docs/AIRFLOW_SETUP.md

**Pipeline Tasks:**
1. **collect_igdb_data** - IGDB API → Local JSON files
2. **upload_to_gcs** - Local files → Google Cloud Storage
3. **load_to_bigquery** - GCS → BigQuery raw tables
4. **run_dbt_transformations** - Raw data → ML-ready features
5. **train_ml_models** - Transformed data → Trained models

### **Fas 5: Vertex AI Learning & Progressive Scaling** ⭐ **NÄSTA** 🎯
**Strategi:** "Local Testing → Vertex AI Learning → Progressive Scaling → Cloud Production"

**Mål:** Lär dig GCP ML-tjänster med våra 100 spel, skala successivt med kvalitetskontroll

#### **Fas 4A: GCP Learning (1-2 dagar)** ✅ **KLAR**
**Syfte:** Lär dig BigQuery, dbt, Airflow, Vertex AI med våra 100 spel

**Steg 1: BigQuery Setup** ✅ **KLAR**
- [x] **Skapa BigQuery dataset** `igdb_games` (exalted-tempo-471613-e2)
- [x] **Ladda upp våra 100 spel** från lokal CSV till BigQuery (games_raw tabell)
- [x] **Testa SQL queries** på speldata i BigQuery (83 kolumner, 100 spel)
- [x] **Skapa views** för genres, platforms, themes (genre_analysis, platform_analysis)

**Steg 2: dbt Project Setup** ✅ **KLAR**
- [x] **Skapa dbt project** för data transformation (`dbt_igdb_project/igdb_models`)
- [x] **Definiera models** för games, genres, platforms (stg_games, game_recommendations)
- [x] **Testa transformations** lokalt med dbt (100 spel transformerade)
- [x] **Deploy till BigQuery** med dbt (US region, igdb_games dataset)

**Steg 3: Airflow DAG Setup** ✅ **KLAR**
- [x] **Skapa Airflow DAG** för data pipeline (igdb_data_pipeline.py)
- [x] **Definiera tasks** för data collection, transformation, ML (5 tasks)
- [x] **Testa DAG** lokalt med Airflow (Web UI på localhost:8080)
- [x] **Deploy till Cloud Composer** (eller lokal Airflow)

**Steg 4: EU Migration & AutoML Pipeline** ✅ **KLAR** / 🔄 **NÄSTA**
- [x] **EU Migration Complete** - BigQuery dataset `igdb_game_data` i EU region
- [x] **EU Storage buckets** - Raw och processed data i europe-west1
- [x] **dbt EU konfiguration** - OAuth authentication fungerar
- [ ] **AutoML integration** för automatisk modellträning
- [ ] **Incremental data collection** för resursoptimering
- [ ] **CI/CD GCP deployment** för production pipeline

---

## 🛠️ **Detaljerad Implementation Guide - Fas 5: Vertex AI Learning**

### **Steg 1: Airflow DAG Testing (1-2 timmar)** 🔄 **NÄSTA**

#### **1.1 Starta Airflow lokalt**
```bash
# Aktivera venv först
source venv/bin/activate

# Starta Airflow
./airflow/start_airflow.sh

# Verifiera att Airflow körs
curl http://localhost:8080/health
```

#### **1.2 Testa Airflow DAG**
**Öppna Airflow Web UI:**
- Gå till http://localhost:8080
- Login: admin / [genererat lösenord från start_airflow.sh]
- Hitta DAG: `igdb_data_pipeline`

**Testa DAG manuellt:**
1. **Klicka på DAG namnet** → `igdb_data_pipeline`
2. **Klicka på "Trigger DAG"** (play-knapp)
3. **Välj "Trigger DAG w/ Config"** för att skicka parametrar
4. **Konfigurera:**
   ```json
   {
     "games_limit": 100,
     "test_mode": true
   }
   ```

**Övervaka körning:**
- **Graph View:** Se task dependencies och status
- **Tree View:** Se historik över körningar
- **Logs:** Klicka på task → "Log" för detaljerade felmeddelanden

#### **1.3 Troubleshooting vanliga problem**
```bash
# Om DAG inte visas:
# Kontrollera att DAG-filen är korrekt placerad
ls -la airflow/dags/igdb_data_pipeline.py

# Om tasks failar:
# Klicka på task → "Log" för att se felmeddelanden
# Vanliga problem:
# - IGDB API credentials saknas
# - GCP service account key saknas
# - Python path problem
```

### **Steg 2: Vertex AI Notebook Setup (1-2 timmar)**

#### **2.1 Aktivera Vertex AI API**
```bash
# Aktivera venv först
source venv/bin/activate

# Aktivera Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verifiera att API är aktiverat
gcloud services list --enabled --filter="name:aiplatform"
```

#### **2.2 Skapa Vertex AI Notebook Instance**
```bash
# Skapa notebook instance
gcloud ai notebooks instances create igdb-ml-notebook \
  --location=europe-west1 \
  --machine-type=e2-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=tf2-2-8-cpu \
  --vm-image-name=tf2-2-8-cpu-20220119-170516

# Öppna notebook
gcloud ai notebooks instances open igdb-ml-notebook --location=europe-west1
```

#### **2.3 Konfigurera Notebook Environment**
```python
# Installera dependencies i notebook
!pip install pandas numpy scikit-learn google-cloud-bigquery

# Konfigurera GCP authentication
from google.cloud import bigquery
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Testa BigQuery connection
client = bigquery.Client()
print("BigQuery connection successful!")
```

### **Steg 3: ML Model Comparison (1-2 timmar)**

#### **3.1 Ladda data från BigQuery**
```python
# Ladda våra 100 spel från BigQuery
query = """
SELECT id, name, summary, rating, genre_id, platform_id, theme_id
FROM `exalted-tempo-471613-e2.igdb_games.game_recommendations`
WHERE summary IS NOT NULL
"""
df = client.query(query).to_dataframe()
print(f"Laddat {len(df)} spel från BigQuery")
```

#### **3.2 Träna content-based model**
```python
# Träna samma modell som lokalt
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
tfidf_matrix = vectorizer.fit_transform(df['summary'].fillna(''))

# Beräkna similarity matrix
similarity_matrix = cosine_similarity(tfidf_matrix)

print(f"Tränat model med {len(df)} spel")
print(f"Similarity matrix shape: {similarity_matrix.shape}")
```

#### **3.3 Jämför prestanda**
```python
# Testa rekommendationer
def get_recommendations(game_id, top_n=3):
    game_idx = df[df['id'] == game_id].index[0]
    similarity_scores = similarity_matrix[game_idx]
    top_indices = similarity_scores.argsort()[-top_n-1:-1][::-1]
    return df.iloc[top_indices][['id', 'name', 'rating']]

# Testa med ett spel
test_game_id = df.iloc[0]['id']
recommendations = get_recommendations(test_game_id)
print("Rekommendationer:")
print(recommendations)
```

### **Steg 4: Progressive Scaling Strategy (2-3 dagar)**

#### **4.1 Skalningsfaser**
**Fas 1: 100 → 1,000 spel (2-3 timmar)**
- Testa lokalt först
- Verifiera data quality
- Jämför ML prestanda

**Fas 2: 1,000 → 10,000 spel (4-6 timmar)**
- Implementera batch processing
- Flytta data till Cloud Storage
- Testa Vertex AI träning

**Fas 3: 10,000 → 100,000+ spel (1-2 dagar)**
- Cloud Functions för parallell data collection
- Vertex AI för distributed ML training
- BigQuery för data processing

#### **4.2 Kvalitetskontroll vid varje steg**
```bash
# Data quality validation
python -c "from src.data_processing.etl_pipeline import ETLPipeline; ETLPipeline().validate_data()"

# ML performance testing
python -c "from src.models.game_recommender import GameRecommender; GameRecommender().train_and_evaluate()"

# Airflow DAG testing
# Kör DAG med nya parametrar och övervaka resultat
```

---

## 🛠️ **Detaljerad Implementation Guide - Fas 4A**

### **Steg 1: BigQuery Setup (2-3 timmar)**

#### **1.1 Aktivera BigQuery API**
```bash
# Aktivera venv först
source venv/bin/activate

# Aktivera BigQuery API
gcloud services enable bigquery.googleapis.com

# Verifiera att API är aktiverat
gcloud services list --enabled --filter="name:bigquery"
```

#### **1.2 Skapa BigQuery Dataset**
```bash
# Skapa dataset för vår data
bq mk --dataset --location=EU --description="IGDB Game Data for ML Pipeline" \
  exalted-tempo-471613-e2:igdb_game_data

# Verifiera att dataset skapades
bq ls exalted-tempo-471613-e2:igdb_game_data
```

#### **1.3 Ladda upp våra 100 spel**
```bash
# Konvertera vår CSV till BigQuery format
python -c "
import pandas as pd
import json

# Läs vår senaste processed data
df = pd.read_csv('data/processed/games_20250910_194944.csv')
print(f'Laddar {len(df)} spel till BigQuery...')

# Spara som JSON för BigQuery
df.to_json('games_for_bigquery.json', orient='records', lines=True)
print('Data konverterad till JSON format')
"

# Ladda upp till BigQuery
bq load --source_format=NEWLINE_DELIMITED_JSON \
  --autodetect \
  exalted-tempo-471613-e2:igdb_game_data.games \
  games_for_bigquery.json

# Verifiera att data laddades
bq query --use_legacy_sql=false "
SELECT COUNT(*) as total_games, 
       COUNT(DISTINCT genre_id) as unique_genres,
       COUNT(DISTINCT platform_id) as unique_platforms
FROM \`exalted-tempo-471613-e2.igdb_game_data.games\`
"
```

#### **1.4 Skapa Views för Analysis**
```bash
# Skapa view för genre analysis
bq query --use_legacy_sql=false "
CREATE OR REPLACE VIEW \`exalted-tempo-471613-e2.igdb_game_data.genre_analysis\` AS
SELECT 
  genre_id,
  COUNT(*) as game_count,
  AVG(rating) as avg_rating,
  MIN(release_year) as earliest_year,
  MAX(release_year) as latest_year
FROM \`exalted-tempo-471613-e2.igdb_game_data.games\`
WHERE genre_id IS NOT NULL
GROUP BY genre_id
ORDER BY game_count DESC
"

# Skapa view för platform analysis
bq query --use_legacy_sql=false "
CREATE OR REPLACE VIEW \`exalted-tempo-471613-e2.igdb_game_data.platform_analysis\` AS
SELECT 
  platform_id,
  COUNT(*) as game_count,
  AVG(rating) as avg_rating,
  MIN(release_year) as earliest_year,
  MAX(release_year) as latest_year
FROM \`exalted-tempo-471613-e2.igdb_game_data.games\`
WHERE platform_id IS NOT NULL
GROUP BY platform_id
ORDER BY game_count DESC
"
```

### **Steg 2: dbt Project Setup (2-3 timmar)** ✅ **KLAR**

#### **2.1 Installera dbt** ✅ **KLAR**
```bash
# Installera dbt med BigQuery support
pip install dbt-bigquery

# Verifiera installation
dbt --version
```

#### **2.2 Skapa dbt Project** ✅ **KLAR**
```bash
# Skapa dbt project
mkdir dbt_igdb_project
cd dbt_igdb_project

# Initiera dbt project
dbt init igdb_models

# Konfigurera profiles.yml för BigQuery
# Dataset: igdb_games (US region)
# Project: exalted-tempo-471613-e2
# Authentication: Service Account
```

#### **2.3 Skapa dbt Models** ✅ **KLAR**

**Staging Model (`stg_games.sql`):**
- Rensar och standardiserar raw games data
- Data quality checks och derived fields
- Rating categories (Excellent, Good, Average, etc.)
- Era categories (Recent, Modern, Classic, Retro)

**Marts Model (`game_recommendations.sql`):**
- ML-optimerad tabell för rekommendationer
- Feature vectors för genre similarity
- Imputed values för missing data
- Processed timestamps för data freshness

#### **2.4 dbt Configuration** ✅ **KLAR**
```yaml
# dbt_project.yml
models:
  igdb_models:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

#### **2.5 Data Tests** ✅ **KLAR**
- Unique constraints på game IDs
- Not-null validations på kritiska fält
- Source data quality tests
- 12/13 tests passerade (1 example test misslyckades)

#### **2.6 Dataset Configuration** ✅ **KLAR**
**BigQuery Datasets:**
- `igdb_games` (US region) - ✅ **AKTIV** - Vår data och dbt models
- `igdb_game_data` (EU region) - ⚠️ **OANVÄND** - Skapad tidigare, kan tas bort

**Region Val:**
- **US region** vald för bättre prestanda med GCP-tjänster
- **EU region** hade krävt extra konfiguration för andra GCP-tjänster
- **Rekommendation:** Behåll US region för konsistens

#### **2.3 Konfigurera dbt Profile**
```bash
# Skapa profiles.yml
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << 'EOF'
igdb_bigquery:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      keyfile: /path/to/your/service-account-key.json
      project: exalted-tempo-471613-e2
      dataset: igdb_game_data
      location: EU
      threads: 4
      timeout_seconds: 300
EOF
```

#### **2.4 Skapa dbt Models**
```bash
# Skapa staging models
mkdir -p models/staging
cat > models/staging/stg_games.sql << 'EOF'
-- Staging model för games data
SELECT 
  id,
  name,
  summary,
  rating,
  release_year,
  genre_id,
  platform_id,
  theme_id,
  created_at,
  updated_at
FROM {{ source('raw', 'games') }}
WHERE name IS NOT NULL
EOF

# Skapa marts models
mkdir -p models/marts
cat > models/marts/game_recommendations.sql << 'EOF'
-- Mart model för game recommendations
SELECT 
  g.id,
  g.name,
  g.summary,
  g.rating,
  g.release_year,
  g.genre_id,
  g.platform_id,
  g.theme_id,
  CASE 
    WHEN g.rating >= 80 THEN 'Excellent'
    WHEN g.rating >= 70 THEN 'Good'
    WHEN g.rating >= 60 THEN 'Average'
    ELSE 'Below Average'
  END as rating_category
FROM {{ ref('stg_games') }} g
WHERE g.rating IS NOT NULL
EOF
```

#### **2.5 Testa dbt**
```bash
# Testa dbt connection
dbt debug

# Kör dbt models
dbt run

# Testa dbt models
dbt test

# Generera dokumentation
dbt docs generate
dbt docs serve
```

### **Steg 3: Airflow DAG Setup (2-3 timmar)**

#### **3.1 Installera Airflow**
```bash
# Installera Airflow
pip install apache-airflow

# Initiera Airflow
airflow db init

# Skapa admin user
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

#### **3.2 Skapa Airflow DAG**
```bash
# Skapa DAGs mapp
mkdir -p ~/airflow/dags

# Skapa IGDB data pipeline DAG
cat > ~/airflow/dags/igdb_data_pipeline.py << 'EOF'
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'igdb-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'igdb_data_pipeline',
    default_args=default_args,
    description='IGDB Game Data Collection and Processing Pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def collect_game_data():
    """Collect game data from IGDB API"""
    import subprocess
    subprocess.run(['python', 'collect_data.py', '--games-limit', '100'], cwd='/path/to/your/project')
    return "Data collection completed"

def process_data():
    """Process collected data"""
    import subprocess
    subprocess.run(['python', '-m', 'src.data_processing.etl_pipeline'], cwd='/path/to/your/project')
    return "Data processing completed"

def train_model():
    """Train ML model"""
    import subprocess
    subprocess.run(['python', '-m', 'src.models.train_recommender'], cwd='/path/to/your/project')
    return "Model training completed"

# Define tasks
collect_task = PythonOperator(
    task_id='collect_game_data',
    python_callable=collect_game_data,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

# Define task dependencies
collect_task >> process_task >> train_task
EOF
```

#### **3.3 Starta Airflow**
```bash
# Starta Airflow webserver
airflow webserver --port 8080 &

# Starta Airflow scheduler
airflow scheduler &

# Öppna Airflow UI
open http://localhost:8080
```

### **Steg 4: Vertex AI Learning (2-3 timmar)**

#### **4.1 Aktivera Vertex AI API**
```bash
# Aktivera Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verifiera att API är aktiverat
gcloud services list --enabled --filter="name:aiplatform"
```

#### **4.2 Skapa Vertex AI Notebook**
```bash
# Skapa Vertex AI notebook instance
gcloud ai notebooks instances create igdb-ml-notebook \
  --location=europe-west1 \
  --machine-type=e2-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=tf2-2-8-cpu \
  --vm-image-name=tf2-2-8-cpu-20220119-170516

# Öppna notebook
gcloud ai notebooks instances open igdb-ml-notebook --location=europe-west1
```

#### **4.3 Testa ML träning i Vertex AI**
```python
# Skapa notebook cell för ML träning
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import bigquery

# Ladda data från BigQuery
client = bigquery.Client()
query = """
SELECT id, name, summary, rating, genre_id, platform_id, theme_id
FROM `exalted-tempo-471613-e2.igdb_game_data.games`
WHERE summary IS NOT NULL
"""
df = client.query(query).to_dataframe()

# Träna enkel content-based model
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['summary'].fillna(''))

# Beräkna similarity matrix
similarity_matrix = cosine_similarity(tfidf_matrix)

print(f"Tränat model med {len(df)} spel")
print(f"Similarity matrix shape: {similarity_matrix.shape}")
```

---

## 🚀 **Skalningsstrategi: 100 → 100,000+ Spel**

### **Kritiska Skalningsutmaningar & Lösningar**

#### **1. Data Collection Bottlenecks** 🔥 **KRITISKT**
**Problem:** IGDB API rate limit (30 req/min) blir flaskhals vid 100,000+ spel
**Lösningar:**
- **Batch Processing:** Samla data i chunks (1000 spel per batch)
- **Parallel Processing:** Använda Cloud Functions för parallell data collection
- **Caching Strategy:** Redis/Memcached för att undvika duplicerade API calls
- **Incremental Updates:** Bara samla nya/uppdaterade spel dagligen

#### **2. Storage & Processing Limits** 💾 **VIKTIGT**
**Problem:** Lokal storage och minne räcker inte för 100,000+ spel
**Lösningar:**
- **Cloud Storage:** GCS buckets för raw data (billigare än BigQuery)
- **Data Partitioning:** Partitionera data per år/genre för snabbare queries
- **Streaming Processing:** Cloud Dataflow för real-time data processing
- **Data Archiving:** Flytta gamla data till Coldline Storage

#### **3. ML Model Performance** 🤖 **KRITISKT**
**Problem:** Cosine similarity på 100,000+ spel blir extremt långsam
**Lösningar:**
- **Vector Databases:** Pinecone/Weaviate för snabba similarity searches
- **Model Optimization:** Använda approximate nearest neighbors (ANN)
- **Feature Selection:** Reducera dimensions med PCA/t-SNE
- **Distributed Training:** Vertex AI för parallell modellträning

#### **4. API Response Times** ⚡ **VIKTIGT**
**Problem:** Rekommendationer tar för lång tid med stora datasets
**Lösningar:**
- **Precomputed Recommendations:** Beräkna rekommendationer i förväg
- **Caching Layer:** Redis för snabba API responses
- **CDN:** CloudFlare för statisk content
- **Database Indexing:** Optimera BigQuery queries med proper indexing

### **Best Practice Architecture för Skalning**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   IGDB API      │───▶│  Cloud Functions │───▶│  Cloud Storage  │
│  (Rate Limited) │    │  (Parallel Jobs) │    │   (Raw Data)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vertex AI     │◀───│   Airflow DAG    │◀───│   BigQuery      │
│  (ML Training)  │    │ (Orchestration)  │    │ (Processed Data)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cloud Run     │◀───│   Redis Cache    │◀───│   Vector DB     │
│  (API Serving)  │    │ (Fast Responses) │    │ (Similarity)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Skalningsfaser**

#### **Fas 1: 100 → 1,000 spel** (Nuvarande)
- ✅ BigQuery setup klar
- 🔄 dbt project för data transformation
- 🔄 Airflow DAG för automation
- 🔄 Basic ML model optimization

#### **Fas 2: 1,000 → 10,000 spel** (Nästa vecka)
- 🔄 Cloud Storage integration
- 🔄 Parallel data collection
- 🔄 Model performance optimization
- 🔄 Caching implementation

#### **Fas 3: 10,000 → 100,000+ spel** (Framtida)
- 🔄 Vector database integration
- 🔄 Distributed ML training
- 🔄 Advanced caching strategies
- 🔄 Production monitoring

---

## 🎯 **Nästa Steg efter Fas 4A**

När du har genomfört Fas 4A kommer du att ha:
- ✅ **BigQuery dataset** med våra 100 spel
- ✅ **dbt project** för data transformation
- ✅ **Airflow DAG** för data pipeline
- ✅ **Vertex AI notebook** för ML experimentation

**Då är du redo för Fas 4B: Local Scaling** med 10,000+ spel!

#### **Fas 4B: Local Scaling (1-2 dagar)** 🔄
**Syfte:** Skala upp till 10,000+ spel lokalt när du förstår GCP

**Steg 1: Data Collection Scaling**
- [ ] **Samla 10,000+ spel** med `collect_data.py --games-limit 10000`
- [ ] **Optimera data collection** för större volymer
- [ ] **Implementera batch processing** för effektivitet
- [ ] **Validera data quality** med större dataset

**Steg 2: ML Algorithm Optimization**
- [ ] **Testa olika ML-algoritmer** med 10,000+ spel
- [ ] **Optimera feature engineering** för prestanda
- [ ] **Implementera model evaluation** med cross-validation
- [ ] **Jämför algoritmer** (content-based vs collaborative)

**Steg 3: Performance Optimization**
- [ ] **Optimera Docker builds** för snabbare deployment
- [ ] **Implementera caching** för API responses
- [ ] **Optimera database queries** för prestanda
- [ ] **Testa load testing** med större datamängder

#### **Fas 4C: Cloud Production (1-2 dagar)** 🚀
**Syfte:** Deploy komplett system till GCP när allt fungerar lokalt

**Steg 1: Cloud Run Deployment**
- [ ] **Deploy frontend** till Cloud Run
- [ ] **Deploy backend** till Cloud Run
- [ ] **Konfigurera Cloud SQL** för PostgreSQL
- [ ] **Testa end-to-end** i molnet

**Steg 2: Data Pipeline Production**
- [ ] **Deploy Airflow DAG** till Cloud Composer
- [ ] **Konfigurera BigQuery** för production data
- [ ] **Deploy dbt models** för data transformation
- [ ] **Automatisera data pipeline** med Airflow

**Steg 3: ML Production**
- [ ] **Deploy ML model** till Vertex AI
- [ ] **Konfigurera model serving** med Cloud Run
- [ ] **Implementera model monitoring** med Vertex AI
- [ ] **Automatisera model retraining** med Airflow

**Steg 4: Production Monitoring**
- [ ] **Sätt upp Cloud Monitoring** för system health
- [ ] **Konfigurera budget alerts** för kostnadskontroll
- [ ] **Implementera logging** med Cloud Logging
- [ ] **Sätt upp error tracking** med Cloud Error Reporting

### **Fas 5: Advanced ML & Production** ⭐ **FRAMTIDA** 🔮
**Mål:** Production-ready system med avancerade funktioner

**Uppgifter:**
- [ ] **Advanced features** - text analysis, visual similarity
- [ ] **A/B testing** framework med frontend integration
- [ ] **User feedback** system för continuous improvement
- [ ] **Real-time rekommendationer** med caching
- [ ] **Performance monitoring** med budget tracking
- [ ] **CI/CD pipeline** med automated testing
- [ ] **Documentation** och presentation för kursen

---

## 📈 **Success Metrics**

### **Tekniska Metrics**
- **API Response Time:** < 200ms för rekommendationer
- **Data Freshness:** Daglig uppdatering av speldata
- **System Uptime:** > 99.5%
- **Model Accuracy:** > 80% relevanta rekommendationer

### **Användarupplevelse Metrics**
- **Search Success Rate:** > 90% hittar sökta spel
- **Recommendation Relevance:** Användarfeedback > 4/5
- **Page Load Time:** < 2 sekunder
- **Mobile Responsiveness:** Fungerar på alla enheter

### **Business Metrics**
- **Data Pipeline Efficiency:** < 1 timme för fullständig datauppdatering
- **Cost Optimization:** < $100/månad i GCP-kostnader (med budget tracking)
- **Scalability:** Stöder 1000+ samtidiga användare
- **Budget Utilization:** < 80% av tillgängliga GCP credits
- **Development Velocity:** Visuell feedback inom 1 dag för varje feature

---

## 🎯 **Nästa Steg - Hybrid GCP Strategy**

### **Omedelbara åtgärder (Idag):**
1. **Fas 4A: GCP Learning** - Börja med BigQuery setup
2. **Ladda upp våra 100 spel** till BigQuery för att lära sig
3. **Skapa dbt project** för data transformation
4. **Testa Airflow DAG** lokalt

### **Denna vecka:**
- **Fas 4A:** GCP Learning (BigQuery, dbt, Airflow, Vertex AI)
- **Fas 4B:** Local Scaling (10,000+ spel lokalt)
- **Fas 4C:** Cloud Production (deploy till GCP)

### **Kommande veckor:**
- **Vecka 4:** Advanced ML och production deployment
- **Vecka 5:** Kurs presentation och dokumentation

---

## 📝 **Projektstatus**

**Senast uppdaterad:** 2025-09-12
**Nuvarande fas:** Fas 5 - AutoML Pipeline & Cloud Production (🔄 Pågående) + EU Migration Complete (✅ Klar)
**Nästa milestone:** Skalbar AutoML pipeline med incremental data collection och CI/CD deployment
**Gruppmedlemmar:** Viktoria, Isak & Johan
**Teknisk stack:** Python, Next.js, shadcn/ui, Docker, GCP, IGDB API
**Budget:** AI24S-Data-Engineering-IGDB (kr100.00/månad) + $300 GCP credits
**GCP Project:** IGDB-ML-Pipeline (exalted-tempo-471613-e2)
**Strategi:** Hybrid GCP Learning → Local Scaling → Cloud Production
**Status:** Komplett fungerande system med 100 spel, ML-rekommendationer, data quality dashboard, Docker containerization och EU GCP migration. Redo för AutoML pipeline och production deployment.

---

## 🚀 **Nästa Steg - AutoML Pipeline & Production Deployment**

### **Fas 5B: Skalbar AutoML Pipeline** 🎯 **NÄSTA**

**Mål:** Implementera automatisk, skalbar ML pipeline som fungerar lika bra med 100 spel som med 10,000+ spel

#### **Steg 1: AutoML Integration (1-2 dagar)**
- [ ] **Konfigurera Vertex AI AutoML** för automatisk modellträning
- [ ] **Integrera AutoML med Airflow DAG** för automatiserad pipeline
- [ ] **Testa AutoML prestanda** med våra 100 spel från BigQuery EU
- [ ] **Jämför AutoML vs manuell ML** för prestanda och kostnad

#### **Steg 2: Incremental Data Collection (1 dag)**
- [ ] **Implementera data freshness tracking** i BigQuery
- [ ] **Optimera IGDB API calls** för att undvika duplicerade requests
- [ ] **Caching strategy** för att spara API rate limits
- [ ] **Batch processing** för effektiv data collection

#### **Steg 3: CI/CD GCP Deployment (1-2 dagar)**
- [ ] **Konfigurera Cloud Build** för automatisk deployment
- [ ] **Deploy frontend till Cloud Run** med Next.js
- [ ] **Deploy backend till Cloud Run** med FastAPI
- [ ] **Konfigurera Cloud SQL** för PostgreSQL production
- [ ] **Sätt upp monitoring** med Cloud Monitoring

#### **Steg 4: Production Monitoring (1 dag)**
- [ ] **Budget alerts** för kostnadskontroll
- [ ] **Performance monitoring** för API response times
- [ ] **Error tracking** med Cloud Error Reporting
- [ ] **Logging** med Cloud Logging

### **Teknisk Arkitektur för Production:**
```
IGDB API → Airflow → BigQuery EU → AutoML → Trained Model → Cloud Run → Next.js Frontend
```

**Fördelar med AutoML:**
- ✅ Automatisk skalning med datamängd
- ✅ Ingen manuell ML-optimering krävs
- ✅ GCP hanterar infrastruktur
- ✅ Konsistent prestanda oavsett data-volym

---

## 🎯 **UPPDATERAD GCP DEPLOYMENT STRATEGI**

### **Kursprojekt-fokus (4 veckor kvar):**
- 🎓 **Behöver fungerande pipeline** för betyg
- 💰 **$300 free credits** - Vill inte bränna i onödan
- 🎯 **100 spel** - Nuvarande dataset, vill expandera senare
- 📚 **Lärande-fokus** - Vill förstå varje steg

### **Kostnadseffektiv approach:**
**Alternativ 1: Enkel Pipeline (Rekommenderat)**
```
IGDB API → Cloud Functions → BigQuery → Cloud Run (FastAPI + Next.js)
```
- **Kostnad:** ~$35/månad
- **Setup-tid:** 1-2 dagar
- **Skalbar:** Fungerar för 100 spel och 334,000 spel

**Alternativ 2: Cloud Composer Pipeline (Senare)**
```
IGDB API → Cloud Functions → BigQuery → dbt → Vertex AI → Cloud Run
```
- **Kostnad:** ~$330/månad
- **Setup-tid:** 3-5 dagar
- **Professionell:** Som verkliga production systems

### **Implementation roadmap:**
1. **Fas 1:** Enkel pipeline med Cloud Functions + Cloud Run
2. **Fas 2:** Expansion till fler spel (1000+)
3. **Fas 3:** Cloud Composer + Vertex AI (valfritt)

### **Nästa steg:**
- ✅ Aktivera GCP APIs
- ✅ Deploya Cloud Function för data collection
- ✅ Sätt upp BigQuery dataset
- ✅ Deploya Cloud Run services
- ✅ Testa hela pipeline

---

*Detta dokument ska uppdateras kontinuerligt under projektets gång för att reflektera nuvarande status, lärdomar och ändringar i planeringen.*
