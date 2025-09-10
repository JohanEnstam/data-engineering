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

### **Fas 1: Lokal Prototyping (Vecka 1-2)**
**Mål:** Fungerande lokalt system

**Uppgifter:**
- [ ] Skapa projektstruktur enligt best practice
- [ ] Migrera Isaks IGDB API kod till `src/api/`
- [ ] Utveckla data collection script
- [ ] Bygg data preprocessing pipeline
- [ ] Skapa enkel ML model (content-based filtering)
- [ ] Testa rekommendationsalgoritm
- [ ] Bygg enkel web interface (Next.js)
- [ ] Skapa FastAPI endpoints
- [ ] Unit tests för kritiska funktioner

**Deliverables:**
- Fungerande lokalt rekommendationssystem
- Basic web interface
- API endpoints för spel-sökning
- Dokumenterad kod

### **Fas 2: Cloud Integration (Vecka 3-4)**
**Mål:** Produktionsklart system i molnet

**Uppgifter:**
- [ ] Skapa GCP projekt och BigQuery dataset
- [ ] Deploy API till Cloud Run
- [ ] Skapa Airflow DAG för data pipeline
- [ ] Automatisera data collection och processing
- [ ] Deploy web app till Cloud Run
- [ ] Sätt upp monitoring och logging
- [ ] CI/CD pipeline med GitHub Actions
- [ ] Performance optimization
- [ ] Security hardening

**Deliverables:**
- Automatiserad data pipeline
- Produktionsklart system i molnet
- CI/CD pipeline
- Monitoring och alerts

### **Fas 3: ML Enhancement (Vecka 5-6)**
**Mål:** Avancerade ML-funktioner

**Uppgifter:**
- [ ] Implementera collaborative filtering
- [ ] Hybrid rekommendationsalgoritm
- [ ] A/B testing av olika modeller
- [ ] Visual similarity (cover analysis)
- [ ] Text analysis (summary sentiment)
- [ ] Model performance monitoring
- [ ] Real-time rekommendationer
- [ ] Caching för performance

**Deliverables:**
- Avancerade ML-algoritmer
- A/B testing framework
- Performance monitoring
- Optimized rekommendationer

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
- **Cost Optimization:** < $50/månad i GCP-kostnader
- **Scalability:** Stöder 1000+ samtidiga användare

---

## 🔧 **Utvecklingsmiljö**

### **Lokal Utveckling**
```bash
# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js environment
cd frontend
npm install
npm run dev

# Docker (optional)
docker-compose up
```

### **Cloud Environment**
- **GCP Project:** igdb-game-recommender
- **BigQuery Dataset:** game_data
- **Cloud Storage:** igdb-raw-data
- **Cloud Run:** API och Frontend
- **Airflow:** Data pipeline orchestration

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
1. **Skapa develop branch** från main
2. **Skapa feature/igdb-project-setup** branch
3. **Migrera Isaks kod** till ny struktur
4. **Sätt upp projektstruktur** enligt best practice
5. **Börja utveckla** första komponenter

### **Kommande veckor:**
- **Vecka 1:** Lokal prototyping och grundläggande funktionalitet
- **Vecka 2:** ML-algoritmer och rekommendationssystem
- **Vecka 3:** Cloud integration och data pipeline
- **Vecka 4:** Production deployment och optimization

---

## 📝 **Projektstatus**

**Senast uppdaterad:** 2024-09-10
**Nuvarande fas:** Projektplanering och setup
**Nästa milestone:** Lokal prototyping (Vecka 1)
**Gruppmedlemmar:** Viktoria, Isak & Johan
**Teknisk stack:** Python, Next.js, GCP, IGDB API

---

*Detta dokument ska uppdateras kontinuerligt under projektets gång för att reflektera nuvarande status, lärdomar och ändringar i planeringen.*
