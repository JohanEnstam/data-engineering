# API Exploration - SMHI & Trafiklab

## 🎯 Syfte
Utforska SMHI's olika API:er och dataset samt Trafiklab's alternativ för att välja optimala datakällor för väderbaserad fördröjningsprediktion i Stockholm.

---

## 🌤️ SMHI API Exploration

### 📊 Nuvarande Implementation
**Använder**: SMHI Observations API (opendata-download-metobs.smhi.se)
- **Parameter 7**: Nederbörd (summa 1 timme)
- **Parameter 1**: Temperatur (momentanvärde)
- **Parameter 8**: Snödjup (momentanvärde)
- **Parameter 4**: Vindhastighet (medelvärde 10 min)

### 🔍 SMHI API Alternativ att Utforska

#### 1. **SMHI Observations API** (Nuvarande)
**URL**: `https://opendata-download-metobs.smhi.se/api/`
**Fördelar**:
- ✅ Historisk data tillgänglig
- ✅ Flera väderparametrar
- ✅ Gratis och öppen
- ✅ Dokumenterad API

**Begränsningar**:
- ⚠️ Uppdateras inte realtid (15-60 min fördröjning)
- ⚠️ Begränsad geografisk täckning
- ⚠️ Kan ha datagaps

#### 2. **SMHI Forecast API**
**URL**: `https://opendata-download-metfcst.smhi.se/api/`
**Fördelar**:
- ✅ Prognosdata (framtida väder)
- ✅ Högupplöst geografiskt
- ✅ Flera tidsintervall (1h, 3h, 6h, 12h)
- ✅ Flera parametrar

**Begränsningar**:
- ⚠️ Prognosdata, inte observationer
- ⚠️ Kan vara mindre exakt än observationer

#### 3. **SMHI Grid API**
**URL**: `https://opendata-download-grid.smhi.se/api/`
**Fördelar**:
- ✅ Rasterdata (grid)
- ✅ Högupplöst geografiskt
- ✅ Flera parametrar
- ✅ Historisk data

**Begränsningar**:
- ⚠️ Mer komplex att använda
- ⚠️ Större filer

#### 4. **SMHI Climate Data API**
**URL**: `https://opendata-download-climate.smhi.se/api/`
**Fördelar**:
- ✅ Långsiktig klimatdata
- ✅ Historisk data
- ✅ Flera tidsintervall

**Begränsningar**:
- ⚠️ Inte realtid
- ⚠️ Mer för klimatanalys

### 🎯 Rekommenderad SMHI Strategi
**Primär**: Observations API (nuvarande) + Forecast API
**Sekundär**: Grid API för mer detaljerad geografisk data

### ✅ SMHI Testresultat
**Observations API**: ✅ Fungerar perfekt
- Temperatur: Stockholm-Observatoriekullen A (station 98230)
- Nederbörd: Stockholm-Observatoriekullen A (station 98230)  
- Vind: Stockholm-Bromma Flygplats (station 97200)
- Snö: Stockholm-Observatoriekullen A (station 98230)

**Forecast API**: ⚠️ Delvis fungerar
- Nederbörd (pmp3g): ✅ 77 tidsintervall tillgängliga
- Temperatur (t): ❌ JSON parsing error
- Vind (ws): ❌ JSON parsing error
- Moln (tcc): ❌ JSON parsing error

---

## 🚌 Trafiklab API Exploration

### 📊 Nuvarande Implementation
**Använder**: SL API via Trafiklab
- Realtidsavgångar (realtimedeparturesV4)
- Reseplanerare (travelplannerV3_1)
- Demo API-nyckel

### 🔍 Trafiklab API Alternativ att Utforska

#### 1. **SL APIs** (Stockholm Lokaltrafik)
**Status**: ✅ Tillgängliga via Trafiklab
**Endpoints**:
- `realtimedeparturesV4` - Realtidsavgångar
- `travelplannerV3_1` - Reseplanerare
- `deviations` - Störningar och avvikelser
- `sites` - Hållplatser

**Fördelar**:
- ✅ Stockholm-specifik
- ✅ Realtidsdata
- ✅ Flera endpoints
- ✅ Dokumenterad

**Begränsningar**:
- ⚠️ Endast Stockholm
- ⚠️ Begränsad historisk data
- ⚠️ API-nyckel krävs

#### 2. **GTFS Sweden 3**
**Status**: 🔍 Behöver undersökas
**Beskrivning**: General Transit Feed Specification för Sverige
**Fördelar**:
- ✅ Standardiserat format
- ✅ Hela Sverige
- ✅ Historisk data
- ✅ Flera transportbolag

**Begränsningar**:
- ⚠️ Kan vara komplex att använda
- ⚠️ Inte realtid
- ⚠️ Begränsad fördröjningsdata

#### 3. **Trafiklab Realtime APIs**
**Status**: 🔍 Behöver undersökas
**Alternativ**:
- ResRobot Realtime
- SL Realtime
- Övriga transportbolag

#### 4. **Trafiklab Historical APIs**
**Status**: 🔍 Behöver undersökas
**Alternativ**:
- ResRobot Historical
- SL Historical
- GTFS Historical

### 🎯 Rekommenderad Trafiklab Strategi
**Primär**: SL APIs (nuvarande) + GTFS Sweden 3
**Sekundär**: ResRobot APIs för bredare täckning

### ✅ Trafiklab Testresultat
**SL API**: ❌ Nätverksproblem
- Realtidsavgångar: ❌ DNS resolution error (api.sl.se)
- Fördröjningsdata: ❌ Samma nätverksproblem
- Orsak: Möjligt nätverksproblem eller felaktig endpoint

**GTFS Sweden 3**: ❌ Endpoints inte tillgängliga
- sweden_3: ❌ 404 Not Found
- stockholm: ❌ 404 Not Found  
- gothenburg: ❌ 404 Not Found
- malmo: ❌ 404 Not Found
- Orsak: Felaktiga endpoints eller API-nyckel krävs

---

## 🔬 Utforskande Testplan

### Phase 1: SMHI API Testing
1. **Testa Forecast API**
   - Implementera forecast data collection
   - Jämför med observations data
   - Utvärdera kvalitet

2. **Testa Grid API**
   - Implementera grid data collection
   - Jämför geografisk upplösning
   - Utvärdera komplexitet

3. **Jämförelseanalys**
   - Datakvalitet
   - Uppdateringsfrekvens
   - Geografisk täckning
   - Komplexitet

### Phase 2: Trafiklab API Testing
1. **GTFS Sweden 3 Investigation**
   - Dokumentation och struktur
   - Geografisk täckning
   - Realtidsdata tillgänglighet
   - Kostnad och tillgång

2. **ResRobot API Testing**
   - Implementera ResRobot collection
   - Jämför med SL APIs
   - Utvärdera täckning

3. **Historical Data Investigation**
   - Tillgänglig historisk data
   - Dataformat och kvalitet
   - Kostnad och tillgång

### Phase 3: Integration Testing
1. **Kombinerad Data Pipeline**
   - SMHI + Trafiklab integration
   - Datasynkronisering
   - Kvalitetskontroll

2. **Performance Testing**
   - API rate limits
   - Response times
   - Data reliability

---

## 📋 Nästa Steg

### Prioritet 1: SMHI Forecast API
- [ ] Implementera forecast data collection
- [ ] Jämför med observations data
- [ ] Utvärdera för prediktionsmodell

### Prioritet 2: GTFS Sweden 3
- [ ] Undersök dokumentation
- [ ] Testa dataaccess
- [ ] Utvärdera geografisk täckning

### Prioritet 3: ResRobot APIs
- [ ] Implementera ResRobot collection
- [ ] Jämför med SL APIs
- [ ] Utvärdera täckning

---

## 💡 Rekommendationer

### SMHI
**Fortsätt med**: ✅ Observations API (fungerar perfekt)
**Förbättra**: Forecast API (fixa JSON parsing errors)
**Undersök**: Grid API för mer detaljerad geografisk data

### Trafiklab
**Fortsätt med**: ⚠️ SL APIs (nätverksproblem att lösa)
**Undersök**: ✅ Korrekta Trafiklab endpoints och API-nycklar
**Alternativ**: ResRobot APIs för bredare täckning

### Integration
**Fokus**: Kombinera SMHI observations med förbättrad forecast data
**Backup**: Undersök alternativa transportdatakällor
**Prioritet**: Lösa Trafiklab nätverksproblem först
