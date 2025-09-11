# Airflow Setup Guide - IGDB Data Pipeline

## 🎯 **Översikt**

Denna guide dokumenterar vår Airflow-implementation för IGDB speldata pipeline. Airflow används för att orkestrera hela dataflödet från IGDB API till ML-modeller.

## 🏗️ **Arkitektur**

```
IGDB API → Cloud Storage → BigQuery → dbt → ML Models
    ↓           ↓            ↓        ↓       ↓
  Airflow    Airflow     Airflow   Airflow  Airflow
   Task      Task        Task      Task     Task
```

### **Data Pipeline Flow:**
1. **Data Collection:** IGDB API → Local JSON files
2. **Storage Upload:** Local files → Google Cloud Storage
3. **BigQuery Load:** GCS → BigQuery raw tables
4. **dbt Transformations:** Raw data → ML-ready features
5. **ML Training:** Transformed data → Trained models

## 📁 **Project Structure**

```
airflow/
├── dags/
│   ├── igdb_data_pipeline.py      # Main production DAG
│   └── test_igdb_pipeline.py      # Test DAG
├── plugins/                        # Custom plugins
├── logs/                          # Airflow logs
├── airflow.cfg                    # Airflow configuration
├── gcp_connection.py              # GCP connection setup
└── start_airflow.sh               # Startup script
```

## 🔧 **Configuration**

### **Airflow Configuration (`airflow.cfg`)**
```ini
[core]
dags_folder = /path/to/airflow/dags
plugins_folder = /path/to/airflow/plugins
base_log_folder = /path/to/airflow/logs
executor = LocalExecutor
sql_alchemy_conn = sqlite:////path/to/airflow.db
load_examples = False
default_timezone = Europe/Stockholm

[webserver]
web_server_port = 8080
base_url = http://localhost:8080
```

### **GCP Configuration**
- **Project ID:** `exalted-tempo-471613-e2`
- **Dataset:** `igdb_games` (US region)
- **Storage Buckets:**
  - `igdb-raw-data-1757587379` (raw data)
  - `igdb-processed-data-1757587387` (processed data)
- **Service Account:** `frontend/src/github-actions-key.json`

## 🚀 **DAGs**

### **1. Main Production DAG (`igdb_data_pipeline`)**

**Schedule:** Daily at midnight
**Tasks:**
- `collect_igdb_data` - Collect data from IGDB API
- `upload_to_gcs` - Upload to Cloud Storage
- `load_to_bigquery` - Load to BigQuery
- `run_dbt_transformations` - Run dbt models
- `train_ml_models` - Train ML models

**Dependencies:**
```
collect_igdb_data → upload_to_gcs → load_to_bigquery → run_dbt_transformations → train_ml_models
```

### **2. Test DAG (`test_igdb_pipeline`)**

**Schedule:** Manual trigger only
**Tasks:**
- `test_data_collection` - Test IGDB API connection
- `test_dbt_connection` - Test dbt setup
- `test_gcp_connection` - Test GCP services

**Dependencies:**
```
[test_data_collection, test_dbt_connection, test_gcp_connection] (parallel)
```

## 🛠️ **Setup Instructions**

### **1. Install Dependencies**
```bash
# Activate virtual environment
source venv/bin/activate

# Install Airflow with Google providers
pip install apache-airflow-providers-google
```

### **2. Initialize Airflow**
```bash
# Set environment variables
export AIRFLOW_HOME=/path/to/airflow

# Initialize database
airflow db migrate

# Create admin user (Airflow 2.x)
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

### **3. Setup GCP Connection**
```bash
# Run GCP connection setup
python airflow/gcp_connection.py
```

### **4. Start Airflow**
```bash
# Option 1: Use startup script
./airflow/start_airflow.sh

# Option 2: Manual start
airflow webserver --port 8080 --daemon
airflow scheduler --daemon
```

## 📊 **Usage**

### **Access Airflow UI**
- **URL:** http://localhost:8080
- **Username:** admin
- **Password:** admin

### **Run DAGs**

**Manual Trigger:**
1. Go to Airflow UI
2. Find your DAG
3. Click "Trigger DAG" button

**CLI Trigger:**
```bash
# Trigger specific DAG
airflow dags trigger igdb_data_pipeline

# Trigger test DAG
airflow dags trigger test_igdb_pipeline
```

**Monitor Tasks:**
```bash
# List DAGs
airflow dags list

# Check task status
airflow tasks list igdb_data_pipeline

# View task logs
airflow tasks log igdb_data_pipeline collect_igdb_data 2025-01-11
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **DAG Not Appearing**
   - Check DAG syntax: `python -c "from airflow.dags.your_dag import dag"`
   - Verify DAG folder path in `airflow.cfg`
   - Check Airflow logs for errors

2. **GCP Authentication Errors**
   - Verify service account key path
   - Check GCP connection setup
   - Ensure proper permissions

3. **dbt Connection Issues**
   - Verify dbt profiles.yml
   - Check BigQuery dataset exists
   - Test dbt debug command

4. **Task Failures**
   - Check task logs in Airflow UI
   - Verify Python dependencies
   - Check file paths and permissions

### **Debug Commands:**
```bash
# Test DAG syntax
python -c "from airflow.dags.igdb_data_pipeline import dag"

# Check Airflow configuration
airflow config list

# Test GCP connection
python -c "from google.cloud import storage; print('GCP OK')"

# Test dbt connection
cd dbt_igdb_project/igdb_models && dbt debug
```

## 📈 **Monitoring**

### **Airflow Metrics:**
- **DAG Runs:** Success/failure rates
- **Task Duration:** Performance monitoring
- **Resource Usage:** CPU, memory, disk
- **Error Rates:** Failed task analysis

### **Data Quality:**
- **Data Volume:** Games collected per run
- **Data Freshness:** Last successful run
- **Transformation Success:** dbt model status
- **ML Model Performance:** Training metrics

## 🎯 **Next Steps**

1. **Production Deployment:** Move to cloud-based Airflow
2. **Monitoring:** Add alerting and notifications
3. **Scaling:** Optimize for larger datasets
4. **CI/CD:** Integrate with GitHub Actions
5. **Security:** Implement proper authentication

## 📚 **Resources**

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Google Providers](https://airflow.apache.org/docs/apache-airflow-providers-google/)
- [dbt Airflow Integration](https://docs.getdbt.com/docs/deploy/airflow)
- [BigQuery Airflow Operators](https://airflow.apache.org/docs/apache-airflow-providers-google/operators/cloud/bigquery.html)

---

**Senast uppdaterad:** 2025-01-11  
**Status:** ✅ Komplett och fungerande  
**Nästa:** Production deployment och monitoring
