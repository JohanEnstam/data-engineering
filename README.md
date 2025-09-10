# 🎮 IGDB Spelrekommendationssystem

Ett komplett spelrekommendationssystem med Google-liknande sökinterface, ML-baserade rekommendationer och real-time dashboard.

## 🎯 Vad systemet gör

- **Sök spel** med autocomplete (som Google)
- **Få rekommendationer** på liknande spel baserat på ML
- **Dashboard** med statistik och data quality
- **Real-time data** från IGDB API

## 🚀 Snabbstart för gruppmedlemmar

### 1. Klona och navigera
```bash
git clone https://github.com/JohanEnstam/data-engineering.git
cd data-engineering
```

### 2. Sätt upp Python environment
```bash
# Skapa virtual environment
python -m venv venv

# Aktivera (välj rätt kommando för ditt OS)
source venv/bin/activate  # Mac/Linux
# ELLER
venv\Scripts\activate     # Windows

# Installera dependencies
pip install -r requirements.txt
```

### 3. Konfigurera IGDB API
```bash
# Kopiera template
cp .env.template .env

# Redigera .env med dina Twitch credentials
nano .env  # eller använd valfri texteditor
```

**Du behöver:**
- Gå till [Twitch Developer Portal](https://dev.twitch.tv)
- Skapa en ny applikation
- Kopiera Client ID och Client Secret
- Klistra in i `.env` filen

### 4. Samla data (5-10 minuter)
```bash
# Viktigt: Aktivera venv först!
source venv/bin/activate && python collect_data.py --games-limit 1000
```

### 5. Starta backend
```bash
# Terminal 1 - Backend
source venv/bin/activate && python -m uvicorn src.api_endpoints.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Starta frontend
```bash
# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### 7. Öppna systemet
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🎮 Användning

### Sök och rekommendationer
1. Gå till http://localhost:3000/recommendations
2. Skriv i sökfältet (t.ex. "space")
3. Klicka på ett spel för att få rekommendationer

### Dashboard
1. Gå till http://localhost:3000
2. Se statistik, data quality och budget info

## 🏗️ Teknisk Stack

- **Backend:** Python, FastAPI, IGDB API
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **ML:** scikit-learn, pandas, numpy
- **Data:** IGDB API (1000+ spel)

## 📁 Projektstruktur

```
data-engineering/
├── src/                       # Python backend
│   ├── api/                   # IGDB API client
│   ├── data_collectors/       # Data collection
│   ├── data_processing/       # ETL pipeline
│   ├── models/                # ML modeller
│   └── api_endpoints/         # FastAPI endpoints
├── frontend/                  # Next.js app
│   ├── src/app/               # Pages
│   └── src/components/        # React components
├── data/                      # Data storage (lokal)
│   ├── raw/                   # Rådata från IGDB
│   ├── processed/             # Bearbetad data
│   └── models/                # Tränade ML-modeller
└── requirements.txt           # Python dependencies
```

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
```bash
# Kontrollera att venv är aktiverat
which python  # Ska visa path till venv/bin/python
source venv/bin/activate && pip install -r requirements.txt
```

### "Connection refused" i frontend
```bash
# Kontrollera att backend körs
curl http://localhost:8000/api/health
```

### "No games found" i sökning
```bash
# Kontrollera att data finns
ls -la data/processed/games_*.csv
# Om tomt, kör data collection igen
source venv/bin/activate && python collect_data.py --games-limit 1000
```

## 📚 Dokumentation

- [Projektöversikt](PROJECT_OVERVIEW.md) - Detaljerad projektbeskrivning
- [Nästa steg](NEXT_STEPS.md) - Utvecklingsplan
- [Setup Guide](SETUP.md) - Detaljerad installationsguide

## 🤝 Bidrag

1. Skapa feature branch: `git checkout -b feature/ditt-namn`
2. Gör ändringar
3. Committa: `git commit -m "Beskrivning"`
4. Pusha: `git push origin feature/ditt-namn`
5. Skapa Pull Request

---

**🎉 Klar! Du ska nu ha ett fungerande spelrekommendationssystem med 1000+ spel och ML-rekommendationer!**