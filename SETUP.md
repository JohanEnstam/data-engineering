# 🚀 Detaljerad Setup Guide

Denna guide hjälper dig att få igång IGDB Spelrekommendationssystemet från grunden.

## 📋 Förutsättningar

### Programvara som behövs
- **Python 3.9+** ([Ladda ner här](https://www.python.org/downloads/))
- **Node.js 18+** ([Ladda ner här](https://nodejs.org/))
- **Git** ([Ladda ner här](https://git-scm.com/))
- **Texteditor** (VS Code, Sublime, etc.)

### IGDB API Access
- **Twitch Developer konto** ([Registrera här](https://dev.twitch.tv))

## 🔧 Steg-för-steg Installation

### Steg 1: Klona projektet
```bash
git clone https://github.com/JohanEnstam/data-engineering.git
cd data-engineering
```

### Steg 2: Sätt upp Python environment

#### Mac/Linux:
```bash
# Skapa virtual environment
python3 -m venv venv

# Aktivera environment
source venv/bin/activate

# Verifiera att det fungerar
which python  # Ska visa: /path/to/data-engineering/venv/bin/python
```

#### Windows:
```bash
# Skapa virtual environment
python -m venv venv

# Aktivera environment
venv\Scripts\activate

# Verifiera att det fungerar
where python  # Ska visa: C:\path\to\data-engineering\venv\Scripts\python.exe
```

### Steg 3: Installera Python dependencies
```bash
# Kontrollera att venv är aktiverat (ska se (venv) i prompten)
pip install -r requirements.txt

# Verifiera installation
pip list | grep pandas  # Ska visa pandas version
```

### Steg 4: Skaffa IGDB API credentials

1. **Gå till Twitch Developer Portal**
   - Besök: https://dev.twitch.tv
   - Logga in med ditt Twitch-konto

2. **Skapa ny applikation**
   - Klicka "Register Your Application"
   - Fyll i:
     - **Name:** IGDB Data Engineering
     - **OAuth Redirect URLs:** http://localhost:3000
     - **Category:** Other
   - Klicka "Create"

3. **Kopiera credentials**
   - **Client ID:** (lång sträng med siffror och bokstäver)
   - **Client Secret:** (klicka "New Secret" och kopiera)

### Steg 5: Konfigurera environment
```bash
# Kopiera template
cp .env.template .env

# Redigera .env filen
nano .env  # eller använd valfri texteditor
```

**Fyll i dina credentials:**
```bash
# IGDB API Credentials
CLIENT_ID=din_client_id_här
CLIENT_SECRET=din_client_secret_här

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Steg 6: Samla data
```bash
# Viktigt: Aktivera venv först!
source venv/bin/activate && python collect_data.py --games-limit 1000

# Detta tar 5-10 minuter och samlar 1000 spel från IGDB
```

**Vad som händer:**
- Hämtar spel från IGDB API
- Bearbetar data med ETL pipeline
- Tränar ML-modell för rekommendationer
- Sparar allt lokalt i `data/` mappen

### Steg 7: Starta backend
```bash
# Terminal 1 - Backend
source venv/bin/activate && python -m uvicorn src.api_endpoints.main:app --host 0.0.0.0 --port 8000 --reload
```

**Du ska se:**
```
INFO:     Will watch for changes in these directories: ['/path/to/data-engineering']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Steg 8: Starta frontend
```bash
# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

**Du ska se:**
```
▲ Next.js 14.0.0
- Local:        http://localhost:3000
- Network:      http://192.168.1.100:3000

✓ Ready in 2.3s
```

### Steg 9: Testa systemet
1. **Öppna webbläsare:** http://localhost:3000
2. **Gå till Recommendations:** http://localhost:3000/recommendations
3. **Testa sökning:** Skriv "space" i sökfältet
4. **Klicka på ett spel** för att få rekommendationer

## 🔍 Verifiering att allt fungerar

### Kontrollera backend
```bash
curl http://localhost:8000/api/health
# Ska returnera: {"status": "healthy"}
```

### Kontrollera data
```bash
ls -la data/processed/games_*.csv
# Ska visa CSV-fil med 1000+ rader
```

### Kontrollera ML-modell
```bash
ls -la data/models/*.pkl
# Ska visa tränad modell-fil
```

## 🚨 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pandas'"
**Lösning:**
```bash
# Kontrollera att venv är aktiverat
which python  # Ska visa venv/bin/python

# Om inte, aktivera venv
source venv/bin/activate

# Installera om dependencies
pip install -r requirements.txt
```

### Problem: "Connection refused" i frontend
**Lösning:**
```bash
# Kontrollera att backend körs
curl http://localhost:8000/api/health

# Om inte, starta backend
source venv/bin/activate && python -m uvicorn src.api_endpoints.main:app --host 0.0.0.0 --port 8000 --reload
```

### Problem: "No games found" i sökning
**Lösning:**
```bash
# Kontrollera att data finns
ls -la data/processed/games_*.csv

# Om tomt, kör data collection igen
source venv/bin/activate && python collect_data.py --games-limit 1000
```

### Problem: "IGDB API error" eller "Authentication failed"
**Lösning:**
```bash
# Kontrollera .env filen
cat .env

# Kontrollera att credentials är korrekta
# Gå tillbaka till Twitch Developer Portal och verifiera
```

### Problem: Frontend visar "Loading..." evigt
**Lösning:**
```bash
# Kontrollera att både backend och frontend körs
# Backend: http://localhost:8000
# Frontend: http://localhost:3000

# Kontrollera browser console för fel
# F12 -> Console tab
```

## 📊 Vad du ska se när allt fungerar

### Dashboard (http://localhost:3000)
- **Games:** 1000+ spel
- **Genres:** 20+ unika genrer
- **Themes:** 30+ unika teman
- **Platforms:** 10+ plattformar

### Recommendations (http://localhost:3000/recommendations)
- **Sökfält:** Fungerar med autocomplete
- **Sökresultat:** Visar spel med cover-bilder
- **Rekommendationer:** Visar 3 liknande spel när du klickar

### API (http://localhost:8000/docs)
- **Swagger UI:** Interaktiv API dokumentation
- **Endpoints:** /api/recommendations/search, /api/recommendations/{id}

## 🎉 Klar!

Du har nu ett komplett fungerande spelrekommendationssystem med:
- ✅ 1000+ spel från IGDB
- ✅ ML-baserade rekommendationer
- ✅ Google-liknande sökinterface
- ✅ Real-time dashboard
- ✅ Fullständig API

**Nästa steg:** Utforska koden, testa rekommendationerna och börja utveckla nya funktioner!

---

**Behöver hjälp?** Skapa en issue på GitHub eller kontakta teamet!
