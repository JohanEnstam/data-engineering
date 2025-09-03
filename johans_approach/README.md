# Johan's Approach - SMHI + Trafiklab GTFS Integration

## 🎯 Syfte
Denna mapp innehåller allt experimentellt arbete för Johan's approach: SMHI väderdata + Trafiklab GTFS transportdata för fördröjningsprediktion i Stockholm.

## 📁 Mappstruktur

```
johans_approach/
├── README.md                    # Denna fil
├── src/                         # Källkod
│   ├── data_collectors/         # API collectors
│   │   ├── smhi_weather.py      # SMHI observations
│   │   ├── smhi_forecast.py     # SMHI forecast
│   │   └── trafiklab_gtfs_collector.py  # GTFS Sweden 3
│   ├── utils/
│   │   └── api_token_manager.py # API usage tracking
│   └── api/
│       └── main.py              # FastAPI endpoints
├── data/                        # Data (exkluderad från git)
│   ├── raw/
│   │   ├── gtfs/               # 2.2GB statisk data
│   │   └── gtfs_rt/            # Realtidsdata
│   └── api_usage.json          # Token tracking
├── api_documentation/           # Nedladdad API-dokumentation
├── tests/                       # Tester
├── explore_apis.py             # API exploration script
├── download_api_docs.py        # Dokumentation downloader
├── quick_test.py               # Snabbtester
├── test_poc.py                 # PoC tester
└── docs/                       # Dokumentation
    ├── API_EXPLORATION.md
    ├── API_DOCUMENTATION_SUMMARY.md
    ├── API_USAGE_GUIDE.md
    ├── EXPLORATION_RESULTS.md
    └── NEXT_PHASE_PLAN.md
```

## 🚀 Snabbstart

### 1. Installera Dependencies
```bash
cd johans_approach
pip install -r ../requirements.txt
```

### 2. Sätt upp API-nycklar
```bash
# Kopiera .env.example till .env och lägg till dina nycklar
cp ../.env.example .env
# Redigera .env med dina Trafiklab API-nycklar
```

### 3. Testa API:er
```bash
python explore_apis.py
```

### 4. Ladda ner GTFS data
```bash
python src/data_collectors/trafiklab_gtfs_collector.py
```

## 📊 Status

### ✅ Fungerar Perfekt
- **SMHI Observations API**: Stockholm väderdata
- **Trafiklab GTFS Sweden 3**: 2.2GB statisk data laddad ner
- **Token Management**: Automatisk API-usage tracking
- **Realtidsdata**: SL ServiceAlerts fungerar

### ⚠️ Behöver Fixas
- **SMHI Forecast API**: JSON parsing errors
- **SL API**: Nätverksproblem (backup till GTFS)

### 📈 API Usage
- **Statisk data**: 1/50 requests (2% av månadsgräns)
- **Realtidsdata**: 1/30000 requests (0.003% av månadsgräns)

## 🔧 Teknisk Stack

- **Weather**: SMHI Observations API (Stockholm station)
- **Transport**: Trafiklab GTFS Sweden 3 (SL operatör)
- **ML**: Random Forest för fördröjningsprediktion
- **API**: FastAPI med Docker support
- **Token Management**: Automatisk spårning

## 🎯 Nästa Steg

1. **Fixa SMHI Forecast API** - JSON parsing errors
2. **Analysera GTFS-data** - Stockholm-specifik information
3. **Integrera väder + transport** - Kombinera datasets
4. **Träna modell** - På riktig historisk data

## ⚠️ Viktiga Noter

- **API Usage**: Var försiktig med requests (50 statisk/månad)
- **Stora filer**: GTFS data är 2.2GB (exkluderad från git)
- **API-nycklar**: Lagrade i .env (exkluderad från git)
- **Token management**: Fungerar automatiskt

---
**Skapad**: 2025-01-03  
**Status**: Experimenterar med SMHI + Trafiklab integration  
**Mål**: Bygga fungerande prediktionsmodell på riktig data
