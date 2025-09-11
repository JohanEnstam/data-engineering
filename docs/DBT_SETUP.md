# dbt Setup Guide - IGDB Game Data Pipeline

## 🎯 **Översikt**

Denna guide dokumenterar vår dbt-implementation för IGDB speldata transformation. dbt (data build tool) används för att transformera raw data i BigQuery till ML-ready features.

## 📊 **Arkitektur**

```
Raw Data (BigQuery) → dbt Staging → dbt Marts → ML Models
```

### **Data Flow:**
1. **Raw Data:** `igdb_games.games_raw` (100 spel, 83 kolumner)
2. **Staging:** `igdb_games.stg_games` (data quality + derived fields)
3. **Marts:** `igdb_games.game_recommendations` (ML-ready features)

## 🏗️ **Project Structure**

```
dbt_igdb_project/
├── igdb_models/
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_games.sql
│   │   ├── marts/
│   │   │   └── game_recommendations.sql
│   │   ├── sources.yml
│   │   └── schema.yml
│   ├── dbt_project.yml
│   └── README.md
```

## 🔧 **Configuration**

### **dbt Profile (`~/.dbt/profiles.yml`)**
```yaml
igdb_models:
  outputs:
    dev:
      dataset: igdb_games
      job_execution_timeout_seconds: 300
      job_retries: 1
      keyfile: /path/to/service-account-key.json
      location: US
      method: service-account
      priority: interactive
      project: exalted-tempo-471613-e2
      threads: 4
      type: bigquery
  target: dev
```

### **dbt Project (`dbt_project.yml`)**
```yaml
name: 'igdb_models'
version: '1.0.0'
profile: 'igdb_models'

models:
  igdb_models:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

## 📋 **Models**

### **1. Staging Model (`stg_games.sql`)**

**Syfte:** Rensa och standardisera raw games data

**Features:**
- Data quality validation
- Rating categories (Excellent, Good, Average, Below Average, Poor)
- Era categories (Recent, Modern, Classic, Retro)
- All genre/theme/platform features preserved

**Data Quality Checks:**
```sql
CASE 
  WHEN name IS NULL THEN 'Missing Name'
  WHEN rating IS NULL THEN 'Missing Rating'
  WHEN release_year IS NULL THEN 'Missing Release Year'
  ELSE 'Valid'
END as data_quality_status
```

### **2. Marts Model (`game_recommendations.sql`)**

**Syfte:** ML-optimerad tabell för rekommendationer

**ML Features:**
- **Genre Vector:** Comma-separated genre features för similarity
- **Imputed Values:** Missing ratings → 0, Missing years → 2020
- **Processed Timestamps:** Data freshness tracking
- **Quality Filtering:** Endast "Valid" data inkluderad

**Genre Vector Example:**
```
"0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,1,1,0,0"
```

## 🧪 **Data Tests**

### **Source Tests (`sources.yml`)**
```yaml
sources:
  - name: raw
    schema: igdb_games
    tables:
      - name: games_raw
        columns:
          - name: id
            tests:
              - unique
              - not_null
```

### **Model Tests (`schema.yml`)**
```yaml
models:
  - name: stg_games
    columns:
      - name: id
        tests:
          - unique
          - not_null
      - name: data_quality_status
        description: "Data quality assessment"
```

## 🚀 **Usage**

### **Run dbt Models**
```bash
# Aktivera venv
source venv/bin/activate

# Navigera till dbt project
cd dbt_igdb_project/igdb_models

# Kör alla models
dbt run

# Testa data quality
dbt test

# Debug connection
dbt debug
```

### **Query Results**
```sql
-- Staging model
SELECT name, rating_category, era_category, data_quality_status
FROM `exalted-tempo-471613-e2.igdb_games.stg_games`
LIMIT 5;

-- Marts model
SELECT name, rating_imputed, genre_vector
FROM `exalted-tempo-471613-e2.igdb_games.game_recommendations`
LIMIT 3;
```

## 📊 **Results**

### **Data Transformation:**
- **Input:** 100 raw games med 83 kolumner
- **Output:** 100 validated games med ML-ready features
- **Data Quality:** 100% "Valid" status
- **Tests:** 12/13 passed (1 example test failed)

### **Performance:**
- **Staging Model:** 2.01s (CREATE VIEW)
- **Marts Model:** 3.27s (CREATE TABLE, 100 rows, 118.3 KiB)
- **Total Runtime:** 6.33s

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Dataset Not Found Error**
   - **Problem:** Wrong region (EU vs US)
   - **Solution:** Update `location: US` in profiles.yml

2. **Authentication Errors**
   - **Problem:** Service account key path incorrect
   - **Solution:** Verify `keyfile` path in profiles.yml

3. **Protobuf Conflicts**
   - **Problem:** gcloud CLI conflicts with dbt
   - **Solution:** Use venv Python for dbt, system Python for gcloud

## 🎯 **Next Steps**

1. **Airflow Integration:** Automatisera dbt runs
2. **ML Pipeline:** Använda genre vectors för similarity
3. **Scaling:** Optimera för 1,000+ spel
4. **Monitoring:** Data quality alerts

## 📚 **Resources**

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt BigQuery Adapter](https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql)

---

**Senast uppdaterad:** 2025-01-11  
**Status:** ✅ Komplett och fungerande  
**Nästa:** Airflow DAG integration
