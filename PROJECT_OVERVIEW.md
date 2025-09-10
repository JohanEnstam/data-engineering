# IGDB Spelrekommendationssystem - Projektöversikt

## 🎯 **Projektmål**

**Huvudmål:** Bygga ett komplett spelrekommendationssystem med IGDB API som datakälla, implementerat som en fullständig data pipeline i Google Cloud Platform.

**Slutprodukt:** En webbapplikation där användare kan skriva in spel-titlar och få rekommendationer på liknande spel baserat på ML-algoritmer.

---

## 🏗️ **Teknisk Arkitektur**

### **Data Pipeline (End-to-End)**
```
IGDB API → Cloud Storage → BigQuery → ML Processing → FastAPI → Next.js Frontend
```

### **Teknisk Stack**
- **Backend:** Python, FastAPI, IGDB API
- **Data Processing:** BigQuery, Cloud Dataflow/dbt
- **ML:** scikit-learn, pandas, numpy
- **Orchestration:** Apache Airflow
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Cloud:** Google Cloud Platform (GCP)
- **CI/CD:** GitHub Actions
- **Containerization:** Docker

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
- Visual features (cover/screenshot analysis) // Känns överdrivet och beräknings-intensivt...
```

### **Modellträning**
- **Lokal utveckling:** sklearn, pandas för prototyping
- **Cloud training:** Vertex AI för stora modeller
- **Evaluation:** Cross-validation, A/B testing
- **Deployment:** Cloud Run för real-time predictions

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

---

## 🏗️ **Projektstruktur**

### **Git Branch Strategy (Git Flow)**
```
main (production)
├── develop (integration)
│   ├── feature/igdb-api-integration
│   ├── feature/frontend-components
│   ├── feature/ml-recommendations
│   ├── feature/cloud-deployment
│   └── feature/data-pipeline
└── hotfix/ (om nödvändigt)
```

### **Mappstruktur**
```
igdb-game-recommender/
├── src/                       # Huvudkod
│   ├── api/                   # IGDB API client
│   ├── data_collectors/       # Data collection scripts
│   ├── data_processing/       # ETL och transformation
│   ├── models/                # ML modeller och algoritmer
│   ├── api_endpoints/         # FastAPI endpoints
│   └── utils/                 # Hjälpfunktioner
├── frontend/                  # Next.js app
│   ├── src/app/               # App Router pages
│   ├── src/components/        # React komponenter
│   ├── src/lib/               # Utilities
│   └── src/hooks/             # Custom hooks
├── data/                      # Data storage
│   ├── raw/                   # Raw IGDB data
│   ├── processed/             # Cleaned data
│   └── models/                # Trained ML models
├── tests/                     # Unit och integration tests
├── docs/                      # Dokumentation
├── config/                    # Konfigurationsfiler
├── scripts/                   # Deployment scripts
├── requirements.txt           # Python dependencies
├── package.json               # Node.js dependencies
├── Dockerfile                 # Container setup
├── docker-compose.yml         # Local development
└── README.md                  # Projekt dokumentation
```

---

## 🚀 **Utvecklingsfaser**

### **Fas 1: Frontend-First Prototyping (Vecka 1)**
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
- [ ] Skapa enkel ML model (content-based filtering)
- [ ] **Frontend integration** - sök + rekommendationer

**Deliverables:**
- [x] Fungerande lokalt rekommendationssystem
- [x] **Interaktiv web interface** för data exploration
- [x] **Budget monitoring** system med GCP integration
- [x] API endpoints för spel-sökning och budget tracking
- [x] **Visual feedback** för budget monitoring och data exploration

### **Fas 2: Core ML Development (Vecka 2)**
**Mål:** Robust rekommendationsmotor med visuell feedback

**Uppgifter:**
- [ ] **Progressive feature engineering** - börja med core features (genres, themes)
- [ ] **Local model training** på MacBook (1000+ spel)
- [ ] **Manual evaluation system** - "Ser dessa rekommendationer rimliga ut?"
- [ ] **Frontend integration** - sök + rekommendationer i UI
- [ ] **Model comparison** - testa olika algoritmer visuellt
- [ ] **Performance optimization** för lokala constraints
- [ ] **Data quality validation** med visuell feedback

**Deliverables:**
- **Fungerande rekommendationsmotor** med visuell interface
- **Model evaluation** framework
- **Optimized local training** pipeline
- **User feedback** system för model improvement

### **Fas 3: Cloud Integration (Vecka 3)**
**Mål:** Skalning till molnet med budget monitoring

**Uppgifter:**
- [x] **GCP budget tracking** - real-time cost monitoring
- [ ] **Larger data collection** (10,000+ spel)
- [ ] **Cloud model training** med Vertex AI
- [ ] **Cost optimization** baserat på budget constraints
- [ ] **Deploy API** till Cloud Run
- [ ] **Automated data pipeline** med Airflow
- [ ] **Performance monitoring** med budget alerts

**Deliverables:**
- **Skalbar data pipeline** i molnet
- **Budget-aware** system med cost monitoring
- **Production-ready** API och frontend
- **Automated** data collection och model training

### **Fas 4: Advanced ML & Production (Vecka 4)**
**Mål:** Production-ready system med avancerade funktioner

**Uppgifter:**
- [ ] **Advanced features** - text analysis, visual similarity
- [ ] **A/B testing** framework med frontend integration
- [ ] **User feedback** system för continuous improvement
- [ ] **Real-time rekommendationer** med caching
- [ ] **Performance monitoring** med budget tracking
- [ ] **CI/CD pipeline** med automated testing
- [ ] **Documentation** och presentation för kursen

**Deliverables:**
- **Production-ready** rekommendationssystem
- **Advanced ML** funktioner med visuell feedback
- **Complete documentation** för kursen
- **Budget-optimized** cloud deployment

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

## 🔧 **Utvecklingsmiljö**

### **Lokal Utveckling**
```bash
# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js environment (Frontend-First Development)
cd frontend
npm install
npm run dev

# Data collection och ML
python collect_data.py --games-limit 1000
python -m src.models.train_recommender

# Docker (optional)
docker-compose up
```

### **Cloud Environment**
- **GCP Project:** igdb-game-recommender
- **BigQuery Dataset:** game_data
- **Cloud Storage:** igdb-raw-data
- **Cloud Run:** API och Frontend
- **Vertex AI:** ML model training
- **Airflow:** Data pipeline orchestration
- **Budget Monitoring:** Real-time cost tracking

---

## 📚 **Dokumentation**

### **Teknisk Dokumentation**
- [ ] API Documentation (OpenAPI/Swagger)
- [ ] Database Schema Documentation
- [ ] ML Model Documentation
- [ ] Deployment Guide
- [ ] Troubleshooting Guide

### **Användardokumentation**
- [ ] User Guide
- [ ] FAQ
- [ ] Video Tutorials
- [ ] Best Practices

---

## 🎯 **Nästa Steg**

### **Omedelbara åtgärder:**
1. **Frontend setup** med Next.js + shadcn/ui
2. **Data visualization** - visa testdata i tables/charts
3. **Budget tracking** dashboard för GCP credits
4. **Basic API endpoints** för data access
5. **Core ML development** med visuell feedback

### **Kommande veckor:**
- **Vecka 1:** Frontend-first prototyping med data visualization
- **Vecka 2:** Core ML development med visuell feedback
- **Vecka 3:** Cloud integration med budget monitoring
- **Vecka 4:** Advanced ML och production deployment

---

## 📝 **Projektstatus**

**Senast uppdaterad:** 2025-09-10
**Nuvarande fas:** Frontend-First Prototyping (✅ Klar) + GCP Budget Integration (✅ Klar)
**Nästa milestone:** Core ML Development (Vecka 2)
**Gruppmedlemmar:** Viktoria, Isak & Johan
**Teknisk stack:** Python, Next.js, shadcn/ui, GCP, IGDB API
**Budget:** $300 GCP credits tillgängliga (med real-time monitoring)
**GCP Project:** IGDB-ML-Pipeline (exalted-tempo-471613-e2)

---

*Detta dokument ska uppdateras kontinuerligt under projektets gång för att reflektera nuvarande status, lärdomar och ändringar i planeringen.*
