# IGDB Spelrekommendationssystem

Ett komplett spelrekommendationssystem byggt med IGDB API, Machine Learning och Google Cloud Platform.

## 🎯 Projektöversikt

Detta projekt bygger ett spelrekommendationssystem där användare kan söka efter spel och få rekommendationer på liknande spel baserat på ML-algoritmer. Systemet använder IGDB API som datakälla och är implementerat som en fullständig data pipeline i Google Cloud Platform.

## 🏗️ Teknisk Stack

- **Backend:** Python, FastAPI, IGDB API
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Data Processing:** BigQuery, Cloud Dataflow/dbt
- **ML:** scikit-learn, pandas, numpy
- **Orchestration:** Apache Airflow
- **Cloud:** Google Cloud Platform (GCP)
- **CI/CD:** GitHub Actions
- **Containerization:** Docker

## 🚀 Snabbstart

### Förutsättningar

- Python 3.11+
- Node.js 18+
- Docker (valfritt)
- Twitch Developer konto för IGDB API

### Lokal utveckling

1. **Klona repositoryt**
```bash
git clone <repository-url>
cd data-engineering
```

2. **Sätt upp Python environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# eller
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Konfigurera environment variabler**
```bash
cp .env.template .env
# Redigera .env med dina Twitch credentials
```

4. **Sätt upp frontend**
```bash
cd frontend
npm install
npm run dev
```

5. **Starta backend**
```bash
python -m uvicorn src.api_endpoints.main:app --reload
```

### Docker utveckling

```bash
# Starta alla tjänster
docker-compose up --build

# Endast backend
docker-compose up api

# Endast frontend
docker-compose up frontend
```

## 📁 Projektstruktur

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
├── data/                      # Data storage
├── tests/                     # Unit och integration tests
├── docs/                      # Dokumentation
├── config/                    # Konfigurationsfiler
├── scripts/                   # Deployment scripts
└── requirements.txt           # Python dependencies
```

## 🔧 Konfiguration

### IGDB API Setup

1. Gå till [Twitch Developer Portal](https://dev.twitch.tv)
2. Skapa en ny applikation
3. Kopiera Client ID och Client Secret
4. Uppdatera `.env` filen

### Environment Variabler

```bash
# IGDB API
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Database (valfritt)
DATABASE_URL=postgresql://user:password@localhost:5432/igdb_recommender

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧪 Testing

```bash
# Kör alla tester
pytest

# Kör specifika tester
pytest tests/test_api.py
pytest tests/test_models.py

# Med coverage
pytest --cov=src tests/
```

## 📊 API Dokumentation

När servern körs, besök:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🚀 Deployment

### Google Cloud Platform

```bash
# Deploy till Cloud Run
gcloud run deploy igdb-api --source .

# Deploy frontend
cd frontend
gcloud run deploy igdb-frontend --source .
```

### Docker

```bash
# Bygg image
docker build -t igdb-recommender .

# Kör container
docker run -p 8000:8000 igdb-recommender
```

## 🤝 Bidrag

1. Forka projektet
2. Skapa en feature branch (`git checkout -b feature/amazing-feature`)
3. Committa dina ändringar (`git commit -m 'Add amazing feature'`)
4. Pusha till branchen (`git push origin feature/amazing-feature`)
5. Öppna en Pull Request


## 📚 Dokumentation

- [Projektöversikt](PROJECT_OVERVIEW.md)
- [Nästa steg](NEXT_STEPS.md)
- [API Dokumentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)

---

*För mer information, se [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)*