# .gitignore Checklist för Grupparbete

## 🎯 Syfte
Säkerställ att alla gruppmedlemmar har samma `.gitignore` för att undvika konflikter.

## ✅ Kritiska Filer Att Exkludera

### 🔑 API-nycklar (KRITISKT)
```
.env
.env.local
.env.production
```
**Varför**: API-nycklar ska aldrig delas eller committas!

### 📊 Stora Datafiler
```
data/raw/gtfs/
data/raw/gtfs_rt/
data/api_usage.json
*.csv
*.json
*.pkl
```
**Varför**: 2.2GB GTFS data + API usage tracking

### 🐍 Python
```
__pycache__/
*.py[cod]
venv/
env/
```
**Varför**: Virtuella miljöer och cache-filer

### 💻 IDE/OS
```
.vscode/
.idea/
.DS_Store
Thumbs.db
```
**Varför**: Personliga inställningar

## 🔄 Synkronisera Med Gruppmedlemmar

### Steg 1: Dela .gitignore
```bash
# Visa din .gitignore
cat .gitignore
```

### Steg 2: Uppdatera Andras .gitignore
```bash
# På varje gruppmedlems dator
git pull origin main
# Kontrollera att .gitignore är uppdaterad
```

### Steg 3: Verifiera
```bash
# Kontrollera att inga känsliga filer är staged
git status
```

## ⚠️ Viktiga Varningar

### För Johan's Branch
- **API Usage**: 1/50 statisk, 1/30000 realtids
- **Stora filer**: GTFS data är 2.2GB
- **Token management**: Fungerar automatiskt

### För Alla Branches
- **Aldrig committa .env filer**
- **Aldrig committa stora datafiler**
- **Använd samma .gitignore struktur**

## 🚀 Nästa Steg
1. **Pusha din branch** - Säkert för andra
2. **Skapa Pull Request** - För diskussion
3. **Dela .gitignore** - Med gruppmedlemmar
4. **Diskutera approach** - Välj gemensam strategi

---
**Mål**: Säker koddelning utan konflikter
