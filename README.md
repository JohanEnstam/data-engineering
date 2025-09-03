# Weather-Based Delay Prediction PoC

Ett Proof of Concept för att förutsäga förseningar i kollektivtrafiken baserat på väderdata.

## Projektbeskrivning

Detta projekt kombinerar väderdata från SMHI Open Data API med kollektivtrafikdata för att förutsäga förseningar. Projektet är byggt som en data pipeline med ML-modell för prediktion.

### Datakällor
- **Väder**: SMHI Open Data API (gratis)
- **Trafik**: Trafiklab APIs (gratis) - placeholder implementation

### Arkitektur
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SMHI API      │    │  Trafiklab API  │    │   ML Model      │
│   (Weather)     │    │   (Traffic)     │    │  (Prediction)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Weather         │    │ Traffic         │    │ FastAPI         │
│ Processor       │    │ Processor       │    │ (REST API)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Installation och körning

### Lokal utveckling

1. **Skapa och aktivera virtuell miljö:**
```bash
python -m venv venv
source venv/bin/activate  # På macOS/Linux
# eller
venv\Scripts\activate    # På Windows
```

2. **Installera dependencies:**
```bash
pip install -r requirements.txt
```

2. **Testa datainsamling:**
```bash
# Testa väderdata
python src/data_collectors/smhi_weather.py

# Testa trafikdata (mock)
python src/data_collectors/trafiklab_api.py
```

3. **Träna modellen:**
```bash
python src/models/delay_predictor.py
```

4. **Starta API:**
```bash
python src/api/main.py
```

**Notera:** Se till att din virtuell miljö är aktiverad (`venv`) innan du kör kommandona.

### Docker

1. **Bygg och kör med Docker Compose:**
```bash
docker-compose up --build
```

2. **Eller bygg Docker image manuellt:**
```bash
docker build -t delay-prediction .
docker run -p 8000:8000 delay-prediction
```

## API Endpoints

### Grundläggande
- `GET /` - Välkomstsida
- `GET /health` - Hälsokontroll
- `GET /docs` - API dokumentation (Swagger)

### Väderdata
- `GET /weather?lat=59.3293&lon=18.0686` - Hämta aktuell väderdata

### Prediktioner
- `POST /predict` - Prediktera försening baserat på väderfeatures
- `GET /predict/weather?lat=59.3293&lon=18.0686` - Prediktera från aktuell väderdata

### Modell
- `POST /train` - Träna modellen
- `POST /load-model` - Ladda förtränad modell

## Exempel på användning

### Prediktera försening
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "temperature_c": -2,
       "precipitation_mm": 8,
       "wind_speed_ms": 12,
       "hour": 8,
       "day_of_week": 1,
       "is_weekend": 0,
       "rush_hour": 1
     }'
```

### Hämta väderdata
```bash
curl "http://localhost:8000/weather?lat=59.3293&lon=18.0686"
```

## Projektstruktur

```
├── johans_approach/             # Johan's experimentella arbete
│   ├── src/                     # Källkod (SMHI + Trafiklab)
│   │   ├── data_collectors/     # API collectors
│   │   ├── utils/               # Utilities (token management)
│   │   └── api/                 # FastAPI endpoints
│   ├── data/                    # Data (2.2GB GTFS + realtidsdata)
│   ├── docs/                    # Dokumentation
│   ├── tests/                   # Tester
│   └── README.md                # Johan's approach dokumentation
├── de_agil_metodik/             # Kursmaterial (separat)
├── README.md                    # Huvudprojekt README
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker setup
├── docker-compose.yml           # Docker compose
└── env.example                  # Exempel .env fil
```

## Nästa steg

### För PoC
1. **Integrera riktig Trafiklab API** - Skaffa API-nyckel och implementera riktig datainsamling
2. **Förbättra ML-modellen** - Använd riktig historisk data för träning
3. **Lägg till fler väderfeatures** - Luftfuktighet, snö, etc.
4. **Implementera monitoring** - Loggning och metrics

### För produktion
1. **Databas integration** - PostgreSQL för persistent storage
2. **Caching** - Redis för API caching
3. **Scheduling** - Cron jobs för regelbunden datainsamling
4. **Monitoring** - Prometheus/Grafana
5. **CI/CD** - GitHub Actions för automatisk deployment

## Teknisk stack

- **Backend**: Python, FastAPI
- **ML**: scikit-learn, pandas, numpy
- **Data**: SMHI API, Trafiklab API
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Logging, Health checks

## Bidrag

Detta projekt är en del av kursen Data Engineering på AI och maskinläringsprogrammet.

