# 🚀 GitHub CI/CD Setup Guide

## 📋 **Steg-för-steg Guide för att aktivera CI/CD**

### **Steg 1: Aktivera GitHub Actions**

1. **Gå till din GitHub repository**
   - Navigera till: `https://github.com/JohanEnstam/data-engineering`
   - Klicka på **"Actions"** tab

2. **Aktivera workflows**
   - GitHub kommer föreslå att aktivera workflows
   - Klicka **"I understand my workflows, go ahead and enable them"**

### **Branch Strategy för CI/CD:**

**Develop Branch (Staging):**
- **Trigger:** Push till `develop` branch
- **Deployment:** Staging miljö på GCP Cloud Run
- **URL:** `https://igdb-frontend-staging-xxx-ew.a.run.app`
- **Syfte:** Testa nya features innan production

**Main Branch (Production):**
- **Trigger:** Push till `main` branch
- **Deployment:** Production miljö på GCP Cloud Run
- **URL:** `https://igdb-frontend-prod-xxx-ew.a.run.app`
- **Syfte:** Live applikation för användare

**Workflow Logic:**
```yaml
# Körs på båda branches
on:
  push:
    branches: [ main, develop ]
    
# Men deployment sker bara på specifika branches
if: github.ref == 'refs/heads/develop'  # Staging
if: github.ref == 'refs/heads/main'     # Production
```

### **Steg 2: Konfigurera GitHub Secrets**

Du behöver lägga till följande secrets i din GitHub repository:

#### **2.1 Gå till Settings → Secrets and variables → Actions**

1. Gå till din repository på GitHub
2. Klicka **Settings** (höger sida)
3. I vänster meny: **Secrets and variables** → **Actions**

#### **2.2 Lägg till följande secrets:**

**Repository Secrets (tillgängliga för alla workflows):**
```
IGDB_CLIENT_ID: [din_twitch_client_id]
IGDB_CLIENT_SECRET: [din_twitch_client_secret]
GCP_PROJECT_ID: exalted-tempo-471613-e2
```

**Environment Secrets (miljöspecifika):**

**För Staging Environment:**
```
GCP_SA_KEY: [din_service_account_key_json]
```

**För Production Environment:**
```
GCP_SA_KEY: [din_service_account_key_json]
```

**Varför denna uppdelning:**
- **Repository Secrets:** Allmänna credentials som alla miljöer behöver
- **Environment Secrets:** Säkerhetskänsliga keys som kan vara olika per miljö

#### **2.3 Skapa Environments (för Environment Secrets):**

1. **Gå till Settings → Environments**
2. **Klicka "New environment"**
3. **Skapa två environments:**
   - **Name:** `staging`
   - **Name:** `production`

4. **För varje environment:**
   - Klicka på environment namnet
   - Lägg till `GCP_SA_KEY` secret
   - Sätt protection rules om du vill (valfritt)

#### **2.4 Hur du får GCP Service Account Key:**

```bash
# Aktivera venv först
source venv/bin/activate

# Installera gcloud CLI (om du inte har det)
# brew install google-cloud-sdk  # Mac
# Eller följ: https://cloud.google.com/sdk/docs/install

# Logga in på GCP
gcloud auth login

# Sätt projekt
gcloud config set project exalted-tempo-471613-e2

# Skapa service account för CI/CD
gcloud iam service-accounts create github-actions \
    --description="Service account for GitHub Actions CI/CD" \
    --display-name="GitHub Actions"

# Ge nödvändiga permissions
gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
    --member="serviceAccount:github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding exalted-tempo-471613-e2 \
    --member="serviceAccount:github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Skapa och ladda ner key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@exalted-tempo-471613-e2.iam.gserviceaccount.com

# Kopiera innehållet från github-actions-key.json
cat github-actions-key.json
```

**Kopiera hela JSON-innehållet och lägg till som `GCP_SA_KEY` secret.**

### **Steg 3: Testa CI/CD Pipeline**

#### **3.1 Committa och pusha ändringar:**

**Viktigt:** GitHub Actions visas bara **efter** att du har pushat `.github/workflows/` filer!

```bash
# Aktivera venv först
source venv/bin/activate

# Lägg till alla nya filer
git add .github/
git add .pre-commit-config.yaml
git add GITHUB_CI_CD_SETUP.md

# Committa
git commit -m "feat: Add GitHub Actions CI/CD pipeline

- Add comprehensive CI/CD workflow with testing and Docker builds
- Add simple CI pipeline for initial testing
- Add pre-commit hooks for code quality
- Add setup guide for GitHub secrets configuration"

# Pusha till develop branch
git push origin develop
```

#### **3.2 Kontrollera att pipeline körs:**

**Efter push kommer du att se:**

1. **Actions tab** - Nu kommer workflows att visas (tidigare var den tom)
2. **Workflow runs** - Automatisk körning vid push
3. **Status badges** - Grön/röd status för varje commit

**Vad som händer automatiskt:**
- **Code Quality** - flake8, black, isort för Python
- **TypeScript Checks** - ESLint för frontend  
- **Docker Builds** - Testar att både frontend och backend bygger
- **Basic Tests** - pytest för alla moduler
- **Deployment** - Till staging (develop) eller production (main)

**Branch-specifik deployment:**
- **Push till `develop`** → Deployar till staging miljö
- **Push till `main`** → Deployar till production miljö

### **Steg 4: Förbättra kodkvalitet (valfritt)**

#### **4.1 Installera pre-commit hooks lokalt:**

```bash
# Aktivera venv först
source venv/bin/activate

# Installera pre-commit
pip install pre-commit

# Installera hooks
pre-commit install

# Testa hooks
pre-commit run --all-files
```

#### **4.2 Lägg till grundläggande tester:**

```bash
# Skapa tests mapp
mkdir -p tests

# Skapa enkel test fil
cat > tests/test_basic.py << 'EOF'
import pytest
import sys
import os

# Lägg till src till Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all main modules can be imported"""
    try:
        from src.api_endpoints.main import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main app: {e}")

def test_basic_functionality():
    """Test basic functionality"""
    assert 1 + 1 == 2

if __name__ == "__main__":
    pytest.main([__file__])
EOF

# Installera pytest
pip install pytest

# Kör tester
python -m pytest tests/ -v
```

### **Steg 5: Cloud Deployment (när du är redo)**

#### **5.1 Aktivera Cloud Run API:**

```bash
# Aktivera venv först
source venv/bin/activate

# Aktivera Cloud Run API
gcloud services enable run.googleapis.com

# Aktivera Container Registry API
gcloud services enable containerregistry.googleapis.com
```

#### **5.2 Testa deployment manuellt:**

```bash
# Bygg och push Docker images
docker build -f Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-backend:latest .
docker build -f frontend/Dockerfile -t gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest ./frontend

# Push till Google Container Registry
docker push gcr.io/exalted-tempo-471613-e2/igdb-backend:latest
docker push gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest

# Deploy till Cloud Run
gcloud run deploy igdb-backend-staging \
  --image gcr.io/exalted-tempo-471613-e2/igdb-backend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8000

gcloud run deploy igdb-frontend-staging \
  --image gcr.io/exalted-tempo-471613-e2/igdb-frontend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 3000
```

---

## 🎯 **Nästa Steg efter CI/CD Setup**

### **Omedelbart (idag):**
1. ✅ Konfigurera GitHub Secrets
2. ✅ Committa och testa CI pipeline
3. ✅ Verifiera att alla builds fungerar

### **Denna vecka:**
1. 🔄 Lägg till fler automatiska tester
2. 🔄 Förbättra kodkvalitet med pre-commit hooks
3. 🔄 Testa Docker builds lokalt

### **Nästa vecka:**
1. 🚀 Deploy till GCP Cloud Run
2. 🚀 Sätt upp staging och production environments
3. 🚀 Implementera budget monitoring i CI/CD

---

## 🚨 **Troubleshooting**

### **"Workflow not running"**
- Kontrollera att du har pushat till `main` eller `develop` branch
- Verifiera att `.github/workflows/` mappen finns i repository

### **"Docker build failed"**
- Testa Docker builds lokalt först:
  ```bash
  docker build -f Dockerfile -t test-backend .
  docker build -f frontend/Dockerfile -t test-frontend ./frontend
  ```

### **"Secrets not found"**
- Kontrollera att secrets är korrekt namngivna
- Verifiera att secrets finns i Settings → Secrets and variables → Actions

### **"GCP permission denied"**
- Kontrollera att service account har rätt permissions
- Verifiera att GCP_PROJECT_ID är korrekt

---

## 📚 **Användbara Resurser**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Pre-commit Hooks](https://pre-commit.com/)

---

**🎉 När du har följt denna guide kommer du att ha en komplett CI/CD pipeline som automatiskt testar, bygger och deployar din IGDB-applikation!**
