# Instruktioner

## 1.
Skapa en ny mapp, (namnge mappen vad du vill), i repot med följande struktur:

```
data-engineering/
├── ...
└── {min_mapp}/             < Din nya mapp
    ├── .env
    ├── requirements.txt
    └── main.py
```

Kopiera över `main.py` och `requirements.txt` från `IsaksTestmapp/IgdbApiScript/` till din mapp.

## 2.
Kopiera följande text till `.env`:

```properties
CLIENT_ID={client id}
CLIENT_SECRET={client secret}
```

1. Logga in eller skapa ett nytt konto på https://dev.twitch.tv
2. Klicka på **Your Console** $\rightarrow$ **Applications** $\rightarrow$ **+ Register Your Application**
3. Fyll i samtliga fält:
    - Name: *valfritt*
    - OAuth Redirect URLs: http://localhost
    - Category: *valfritt*
    - Client Type: Confidential
4. Klicka på **Create**
5. Klicka på **Manage** på din registrerade applikation
6. Byt ut `{client id}` i `.env` mot texten under *Client ID* på webbsidan
7. På webbsidan, klicka på **New Secret** och klicka på **OK** i popup-fönstret
8. Byt ut `{client secret}` i `.env` mot den genererade secret-texten på webbsidan

## 3.
Installera alla bibliotek från `requirements.txt`. (Se till att du är i rätt directory och att din venv är aktiverad.)

Beroende på vilken mapp du är i, kör i Ubuntu antingen

```bash
pip install -r requirements.txt
```

*eller*

```bash
pip install -r {min_mapp}/requirements.txt
```

där `{min_mapp}` byts ut mot namnet på mappen som du skapade i steg 1.

## 4.
Gå in i `main.py` och skrolla ner till `def main()`. I funktionen ser du följande rader:

```python
# Fetch data from the IGDB API. 
# Change url, data_fields, and data_limit as needed.
my_data.api_fetch("https://api.igdb.com/v4/games", 
                  client_id, auth["access_token"], 
                  ["name", "rating", "release_dates"], 5)
```

Här kan du byta ut `"https://api.igdb.com/v4/games"` mot en annan godtycklig endpoint-URL som du kan hitta på https://api-docs.igdb.com under *Endpoints*.

Om du byter ut URL:en, se till att byta ut `["name", "rating", "release_dates"]` mot en lista med strängar som finns under *field* i endpoint-tabellen som syns på webbsidan.

Du kan också byta ut `5` mot en annan integer för att välja hur många rader du vill hämta från API:n.

Nu kan du köra `main.py` och se den hämtade json-filen i terminalen. Beroende på vilken mapp du är i, kör antingen

```bash
python3 main.py
```

*eller*

```bash
python3 {min_mapp}/main.py
```

där `{min_mapp}` byts ut mot namnet på mappen du skappade i steg 1.