# IGDB Data Collection & ETL Pipeline

## 🎯 **Översikt**
Detta dokument beskriver hur man använder data collection och ETL pipeline för IGDB spelrekommendationssystemet.

## 📁 **Projektstruktur**
```
data/
├── raw/                    # Rådata från IGDB API
│   ├── games_*.json       # Speldata
│   ├── genres_*.json      # Genrer
│   ├── platforms_*.json   # Plattformar
│   ├── themes_*.json      # Teman
│   └── collection_metadata_*.json
├── processed/             # Processad data för ML
│   ├── games_*.csv       # Speldata (CSV format)
│   ├── games_*.json      # Speldata (JSON format)
│   ├── etl_metadata_*.json
│   └── validation_report_*.txt
└── models/               # Tränade ML-modeller
```

## 🚀 **Snabbstart**

### **1. Installera Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Konfigurera Environment**
```bash
# Kopiera .env.template till .env
cp .env.template .env

# Redigera .env med dina Twitch credentials
# CLIENT_ID=your_client_id
# CLIENT_SECRET=your_client_secret
```

### **3. Kör Data Collection Pipeline**
```bash
# Hämta 1000 spel (default)
python collect_data.py

# Hämta specifikt antal spel
python collect_data.py --games-limit 5000

# Hoppa över data collection, kör endast ETL
python collect_data.py --skip-collection

# Hoppa över ETL, kör endast data collection
python collect_data.py --skip-etl
```

## 📊 **Data Collection**

### **IGDBDataCollector**
Hämtar data från IGDB API och sparar som JSON.

**Funktioner:**
- `collect_games()` - Hämtar speldata
- `collect_genres()` - Hämtar genrer
- `collect_platforms()` - Hämtar plattformar
- `collect_themes()` - Hämtar teman
- `collect_all_data()` - Hämtar all data

**Exempel:**
```python
from src.data_collectors.igdb_data_collector import IGDBDataCollector

collector = IGDBDataCollector()
saved_files = collector.collect_all_data(games_limit=1000)
```

## 🔄 **ETL Pipeline**

### **IGDBETLPipeline**
Transformarar rådata till ML-kompatibelt format.

**Funktioner:**
- `process_games()` - Processar speldata
- `create_genre_features()` - Skapar genre features
- `create_theme_features()` - Skapar theme features
- `create_platform_features()` - Skapar platform features
- `run_full_etl()` - Kör fullständig ETL

**Exempel:**
```python
from src.data_processing.etl_pipeline import IGDBETLPipeline

pipeline = IGDBETLPipeline()
result = pipeline.run_full_etl()
```

## ✅ **Data Validation**

### **IGDBDataValidator**
Validerar data quality och consistency.

**Funktioner:**
- `validate_games_data()` - Validerar speldata
- `validate_feature_consistency()` - Validerar features
- `generate_data_report()` - Genererar rapport
- `save_validation_report()` - Sparar rapport

**Exempel:**
```python
from src.data_processing.data_validator import IGDBDataValidator

validator = IGDBDataValidator()
report = validator.generate_data_report(df)
```

## 📈 **Data Quality Metrics**

### **Obligatoriska Kontroller**
- ✅ Unika ID:n
- ✅ Obligatoriska kolumner
- ✅ Rating range (0-100)
- ✅ Release year validity

### **Feature Consistency**
- ✅ Genre features
- ✅ Theme features
- ✅ Platform features

### **Data Statistics**
- Total antal spel
- Genre distribution
- Theme distribution
- Platform distribution
- Missing data analysis

## 🔧 **Konfiguration**

### **Environment Variables**
```bash
# .env
CLIENT_ID=your_twitch_client_id
CLIENT_SECRET=your_twitch_client_secret
```

### **Data Collection Settings**
```python
# collect_data.py
--games-limit 1000        # Antal spel att hämta
--skip-collection         # Hoppa över data collection
--skip-etl               # Hoppa över ETL
--skip-validation         # Hoppa över validation
```

## 📝 **Logging**

Alla scripts använder Python logging:
- **INFO:** Normal operation
- **WARNING:** Potentiella problem
- **ERROR:** Kritiska fel

Loggar visas i konsolen och kan sparas till fil.

## 🚨 **Troubleshooting**

### **Vanliga Problem**

**1. Authentication Error**
```
Error: invalid client
```
**Lösning:** Kontrollera CLIENT_ID och CLIENT_SECRET i .env

**2. Rate Limit Exceeded**
```
Error: Rate limit exceeded
```
**Lösning:** Vänta 1 minut innan nästa försök

**3. No Data Found**
```
Error: Ingen data hittades
```
**Lösning:** Kontrollera API connection och credentials

**4. Memory Error**
```
Error: Memory error
```
**Lösning:** Minska games-limit eller använd mindre dataset

### **Debug Mode**
```bash
# Aktivera debug logging
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python collect_data.py
```

## 📚 **API Referens**

### **IGDB API Endpoints**
- `games` - Speldata
- `genres` - Genrer
- `platforms` - Plattformar
- `themes` - Teman

### **Rate Limits**
- ~30 requests per minute
- Använd `time.sleep()` mellan requests

### **Data Fields**
Se `src/api/igdb_client.py` för tillgängliga fält.

## 🎯 **Nästa Steg**

Efter data collection:
1. **ML Model Training** - Träna rekommendationsmodeller
2. **API Development** - Bygga FastAPI endpoints
3. **Frontend Development** - Bygga Next.js app
4. **Cloud Deployment** - Deploya till GCP

---

**Senast uppdaterad:** 2024-09-10
**Version:** 1.0.0
