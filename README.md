# ✈️ Telegram Travel Bot: Voli Low Cost, Errori di Prezzo & Pacchetti Vacanze 24/7 (Monetizzato)

Un bot Telegram completamente autonomo e pronto per la produzione che scandaglia ogni ora, 24 ore su 24, le migliori fonti mondiali e italiane di viaggi, rileva **errori di prezzo (Error Fares)**, **voli low-cost**, **pacchetti vacanze volo+hotel** e pubblica **guide di viaggio salva-portafoglio**, monetizzando automaticamente ogni click con i tuoi link di affiliazione.

---

## 🌟 Funzionalità Principali

- ⚡ **Monitoraggio 24/7 Ogni Ora**: Loop asincrono automatico con `APScheduler` che controlla continuamente nuovi feed ed esegue la pubblicazione senza alcun intervento umano.
- 🚨 **Rilevatore di Errori di Prezzo (Error Fares)**: Canale preferenziale e priorità massima per bug tariffari aerei, tratte intercontinentali a prezzi stracciati e tariffe anomale.
- 🏝️ **Pacchetti Vacanze & Weekend**: Estrazione di pacchetti completi Volo + Hotel (Santorini, capitali europee, resort e offerte last-minute).
- 📖 **Guide di Viaggio & Trucchi di Risparmio**: Pubblicazione automatica di mini-guide a rotazione (come viaggiare col solo bagaglio a mano gratuito Ryanair, come ottenere 600€ di rimborso per voli in ritardo, trucchi segreti per Booking.com).
- 💰 **Monetizzazione Automatica Multi-Piattaforma**:
  - **TravelPayouts** (Aviasales, WayAway, Kiwi, Trip.com) per voli e biglietti aerei.
  - **Booking.com Affiliate** per hotel e strutture ricettive nella destinazione.
  - **Civitatis / GetYourGuide** per tour guidati e ingressi prioritari.
  - **Amazon Associates** per zaini da cabina omologati, pesavaligie, organizer e powerbank nelle guide.
- 🛡️ **Deduplicazione SQLite**: Database SQLite integrato che registra l'hash univoco di ogni offerta per non pubblicare mai lo stesso post due volte.
- 🤖 **Bot Telegram Interattivo**: Risponde anche ai messaggi privati con comandi dedicati: `/start`, `/offerte`, `/errori`, `/pacchetti`, `/guide`, `/stats`.

---

## 🚀 Guida Rapida all'Installazione

### 1. Requisiti di Sistema
- Python 3.10, 3.11 o 3.12 (oppure `uv`)
- Connessione a Internet

### 2. Installazione delle dipendenze
Se utilizzi `uv` (consigliato per velocità):
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Oppure con `pip` standard:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Configurazione Telegram & Affiliazioni (`.env`)

Copia il file `.env.example` in `.env`:
```bash
cp .env.example .env
```

Modifica `.env` con i tuoi dati:

### A. Creazione del Bot su Telegram
1. Apri Telegram e cerca **`@BotFather`**.
2. Invia il comando `/newbot` e segui le istruzioni per dare un nome e un username al tuo bot.
3. Copia il **Token HTTP API** generato e incollalo in `TELEGRAM_BOT_TOKEN`.

### B. Canale Telegram
1. Crea un Canale Telegram pubblico (es. `@OfferteVoliLowCostItalia`).
2. Entra nelle impostazioni del Canale -> **Amministratori** -> **Aggiungi Amministratore** -> Cerca il tuo bot e aggiungilo con il permesso di **Pubblicare Messaggi**.
3. Inserisci l'username del canale in `TELEGRAM_CHANNEL_ID` (es. `@OfferteVoliLowCostItalia`).

### C. Codici di Affiliazione (Monetizzazione)
Iscriviti ai programmi gratuiti di affiliazione per generare le tue commissioni:
- **Travelpayouts**: Iscriviti su [travelpayouts.com](https://www.travelpayouts.com) e copia il tuo `Marker` (es. `500000`) in `TRAVELPAYOUTS_MARKER`.
- **Booking.com**: Iscriviti al programma affiliati di Booking e inserisci il tuo `aid` in `BOOKING_AID`.
- **Civitatis**: Inserisci il tuo Partner ID in `CIVITATIS_AFFILIATE_ID`.
- **Amazon Associates**: Inserisci il tuo tag Amazon (es. `tuotag-21`) in `AMAZON_AFFILIATE_TAG`.

---

## 🕹️ Utilizzo & Comandi

### 1. Test Rapido (Scan Immediato)
Esegue un solo ciclo di scansione delle offerte reali e stampa a schermo le schede generate e i pulsanti monetizzati:
```bash
.venv/bin/python main.py --scan-once
```

### 2. Test delle Guide di Viaggio
Visualizza l'anteprima di una guida di viaggio monetizzata con accessori consigliati:
```bash
.venv/bin/python main.py --test-guides
```

### 3. Esecuzione Test Automatici
```bash
.venv/bin/pytest -v
```

### 4. Avvio in Produzione 24/7

#### Opzione A: Script in Background (macOS / Linux)
```bash
./deploy/run_background.sh
```
I log verranno salvati in tempo reale su `logs/bot.log`. Per verificare i log:
```bash
tail -f logs/bot.log
```

#### Opzione B: Docker
```bash
docker build -t telegram-travel-bot -f deploy/Dockerfile .
docker run -d --name travelbot --restart always --env-file .env telegram-travel-bot
```

#### Opzione C: Servizio Systemd (VPS Ubuntu/Debian)
Copia il file `deploy/travelbot.service` in `/etc/systemd/system/`:
```bash
sudo cp deploy/travelbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable travelbot
sudo systemctl start travelbot
```

---

## 📱 Comandi Bot per gli Utenti

Quando un utente contatta il bot in chat privata:
- `/start` - Messaggio di benvenuto con pulsanti rapidi al canale e sezioni
- `/offerte` - Ultime offerte verificate salvate nel database
- `/errori` - Filtro esclusivo sugli errori di prezzo (Error Fares)
- `/pacchetti` - Offerte volo + hotel e resort completi
- `/guide` - Indice interattivo delle guide di viaggio e trucchi di risparmio
- `/stats` - Statistiche sul numero di offerte scovate h24

---

## 📂 Struttura del Progetto

```
telegram-travel-bot/
├── config.py              # Gestore impostazioni (.env, affiliate tags, intervalli)
├── database.py            # SQLite database per deduplicazione e storico
├── classifier.py          # Riconoscimento intelligente categorie, tratte ed error fares
├── monetization.py        # Motore di trasformazione link di affiliazione
├── formatter.py           # Formattatore grafico schede Telegram con emoji e hashtag
├── guide_manager.py       # Archivio guide di viaggio pratiche ad alta conversione
├── bot.py                 # Handlers dei comandi Telegram interattivi (aiogram)
├── worker.py              # Worker asincrono 24/7 di fetch, filtro e pubblicazione
├── main.py                # Entrypoint principale con scheduler e bot polling
├── sources/
│   ├── base_source.py     # Interfaccia sorgente
│   └── feed_sources.py    # Integratore feed (Fly4free, Piratinviaggio, TravelFree, ecc.)
├── deploy/
│   ├── Dockerfile         # Immagine Docker di produzione
│   ├── travelbot.service  # Configurazione systemd per VPS Linux
│   └── run_background.sh  # Script di avvio nohup in background
└── tests/                 # Suite di test automatizzati pytest
```
