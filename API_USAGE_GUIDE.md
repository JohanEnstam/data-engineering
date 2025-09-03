# API Usage Guide - Trafiklab GTFS Sweden 3

## 🎯 Syfte
Denna guide beskriver hur vi hanterar API-anrop försiktigt för att undvika att överskrida begränsningar.

---

## 📊 API Begränsningar

### GTFS Sweden 3 Static Data
- **Bronze**: 50 requests per månad
- **Silver**: 250 requests per månad  
- **Gold**: 1000 requests per månad
- **Uppdatering**: Daglig (05:00-06:00)

### GTFS Sweden 3 Realtime Data
- **Bronze**: 30,000 requests per månad
- **Silver**: 2,000,000 requests per månad
- **Gold**: 22,500,000 requests per månad
- **Uppdatering**: Var 15:e sekund

---

## 🔧 Token Management System

### Automatisk Spårning
- Alla API-anrop spåras automatiskt
- Användning sparas i `data/api_usage.json`
- Varningar visas vid 80% och 100% användning

### Begränsningar
- Statisk data: **KRITISKT** - Endast 50 requests/månad
- Realtidsdata: **Försiktigt** - 30,000 requests/månad

---

## 📋 Best Practices

### Statisk Data (KRITISKT)
1. **Ladda ner EN gång per dag** (05:00-06:00)
2. **Spara lokalt** - Återanvänd data
3. **Testa försiktigt** - Varje test kostar 1 request
4. **Undvik loops** - Kontrollera användning innan

### Realtidsdata (Försiktigt)
1. **Begränsa frekvens** - Max var 15:e sekund
2. **Filtrera operatörer** - Endast SL för Stockholm
3. **Caching** - Spara data lokalt
4. **Monitoring** - Övervaka användning

---

## 🚨 Varningar

### Statisk Data
- **50 requests/månad** = ~1-2 requests/dag
- **Varje test** = 1 request
- **Varje download** = 1 request
- **Risk**: Lätt att bränna igenom alla requests

### Realtidsdata  
- **30,000 requests/månad** = ~1000 requests/dag
- **Varje anrop** = 1 request
- **Risk**: Kan bränna igenom vid buggig kod

---

## 📁 Filstruktur

```
.env                          # API-nycklar
data/
├── api_usage.json           # Spårning av användning
├── raw/
│   ├── gtfs/               # Statisk GTFS data
│   └── gtfs_rt/            # Realtidsdata
└── processed/              # Bearbetad data
```

---

## 🔍 Monitoring

### Användningsöversikt
```bash
python src/utils/api_token_manager.py
python src/data_collectors/trafiklab_gtfs_collector.py
```

### Kontrollera innan anrop
```python
from utils.api_token_manager import token_manager

if token_manager.can_make_request('gtfs_sweden_3_static'):
    # Gör anrop
    pass
else:
    print("API limit reached!")
```

---

## ⚠️ Viktiga Regler

### 1. Statisk Data
- **ALDRIG** i loops
- **ALDRIG** i automatiska tester
- **EN gång per dag** max
- **Spara och återanvänd**

### 2. Realtidsdata
- **Max var 15:e sekund**
- **Endast nödvändiga operatörer**
- **Caching obligatoriskt**
- **Monitoring aktivt**

### 3. Testning
- **Mock data** för utveckling
- **Riktiga API-anrop** endast för produktion
- **Kontrollera användning** före varje test

---

## 🛠️ Felsökning

### "API limit reached"
1. Kontrollera `data/api_usage.json`
2. Vänta till nästa månad
3. Använd mock data för utveckling

### "API key not found"
1. Kontrollera `.env` fil
2. Verifiera variabelnamn
3. Starta om Python-processen

---

## 📈 Uppgradering

### Bronze → Silver
- Statisk: 50 → 250 requests/månad
- Realtids: 30k → 2M requests/månad
- Kostnad: Kontakta Trafiklab

### Silver → Gold  
- Statisk: 250 → 1000 requests/månad
- Realtids: 2M → 22.5M requests/månad
- Kostnad: Kontakta Trafiklab

---

**Status**: ✅ Token management implementerat  
**Nästa**: Testa med riktiga API-nycklar
