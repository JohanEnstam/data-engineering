# 📊 Data Directory Structure

This directory contains all data files for the IGDB Game Recommendation System.

## 📁 Directory Structure

```
data/
├── raw/           # Original IGDB API data (untouched)
├── processed/     # ETL-processed data (ML-ready)
├── external/      # External datasets (not from IGDB)
├── interim/       # Intermediate processing files
├── archive/       # Archived/old datasets
└── models/        # Trained ML models
```

## 📋 Data Types

### Raw Data (`raw/`)
- **Source**: IGDB API via Twitch OAuth2
- **Format**: JSON files with timestamps
- **Naming**: `{data_type}_{timestamp}.json`
- **Examples**:
  - `games_20250910_101521.json`
  - `genres_20250910_101521.json`
  - `platforms_20250910_101521.json`

### Processed Data (`processed/`)
- **Source**: ETL pipeline from raw data
- **Format**: CSV, JSON, and metadata files
- **Naming**: `{data_type}_{timestamp}.{ext}`
- **Examples**:
  - `games_20250910_101632.csv` (ML-ready features)
  - `games_20250910_101632.json` (structured data)
  - `etl_metadata_20250910_101632.json` (processing info)
  - `validation_report_20250910_101632.txt` (quality report)

### External Data (`external/`)
- **Source**: Third-party datasets
- **Purpose**: Additional features or validation
- **Examples**:
  - Steam reviews
  - Metacritic scores
  - User ratings

### Interim Data (`interim/`)
- **Source**: Intermediate processing steps
- **Purpose**: Temporary files during ETL
- **Cleanup**: Automatically cleaned after processing

### Archive (`archive/`)
- **Source**: Old or deprecated datasets
- **Purpose**: Historical reference
- **Retention**: 90 days

### Models (`models/`)
- **Source**: Trained ML models
- **Format**: `.pkl`, `.joblib`, `.onnx`
- **Naming**: `{model_type}_{version}_{timestamp}.{ext}`
- **Examples**:
  - `recommendation_v1.0_20250910.pkl`
  - `similarity_v1.0_20250910.joblib`

## 🔄 Data Flow

```
IGDB API → raw/ → ETL Pipeline → processed/ → ML Training → models/
                ↓
            interim/ (temporary)
                ↓
            archive/ (old data)
```

## 📊 Data Quality

All processed data includes:
- **Validation reports**: Quality metrics and issues
- **ETL metadata**: Processing timestamps and parameters
- **Schema validation**: Type checking and constraints

## 🚀 Usage

### Collecting Data
```bash
# Collect new data
make collect-data

# Collect small dataset for testing
make collect-small
```

### Processing Data
```bash
# Run ETL pipeline
python -m src.data_processing.etl_pipeline

# Validate data quality
python -m src.data_processing.data_validator
```

### Accessing Data
```python
# Load processed games
import pandas as pd
games = pd.read_csv('data/processed/games_latest.csv')

# Load via API
import requests
response = requests.get('http://localhost:8000/api/games')
games = response.json()
```

## 🔒 Security & Privacy

- **No PII**: No personally identifiable information stored
- **Public Data**: Only publicly available game information
- **API Keys**: Stored in environment variables, not in data files
- **Access Control**: Data directory not committed to Git

## 📈 Monitoring

- **File sizes**: Monitored for storage usage
- **Data freshness**: Timestamps tracked
- **Quality metrics**: Validation reports generated
- **Storage costs**: GCP billing integration (future)

## 🧹 Maintenance

### Automatic Cleanup
- Interim files: Cleaned after ETL completion
- Archive files: Cleaned after 90 days
- Log files: Rotated weekly

### Manual Cleanup
```bash
# Clean temporary files
make clean

# Clean all data (WARNING: removes all data!)
make clean-data
```

## 📚 Documentation

- **Data Dictionary**: `docs/data-dictionary.md`
- **API Schema**: `docs/api-schema.md`
- **ETL Pipeline**: `docs/etl-pipeline.md`
- **ML Models**: `docs/ml-models.md`
