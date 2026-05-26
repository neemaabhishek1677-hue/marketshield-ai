# MarketShield AI

**AI-Based Market Manipulation & Insider Trading Detection Platform**

A market surveillance workstation that detects trade anomalies, sentiment-driven manipulation, pump-and-dump risk, and insider-linked trading clusters — with explainable alerts and interactive investigation views.

**Now upgraded with real market data, company news, and SEC filings powered by Finnhub and SEC EDGAR APIs.**

> **Disclaimer:** This is a **surveillance-support prototype**. Outputs are signals for research and compliance review — **not** legal conclusions, investment advice, or proof of wrongdoing.

---

## 🆕 Real Data Upgrade (May 2026)

This platform has been upgraded from **fully synthetic data** to **hybrid real-data mode**:

| Component | Data Source | Real? |
|-----------|------------|-------|
| Stock prices & volume | Finnhub API | ✅ Yes |
| Company news | Finnhub API | ✅ Yes |
| Corporate filings & events | SEC EDGAR | ✅ Yes |
| Market sentiment | Real headlines + VADER NLP | ✅ Yes |
| Trader/entity relationships | NetworkX synthetic graph | ⚠️ Hybrid |
| Trading activity | Synthetic pattern generation | ⚠️ Simulated* |

*Account-level trading data is not publicly available; the platform uses real market context (prices, news, events) combined with simulated trader behavior to demonstrate surveillance logic.

### What Changed

1. **Real Market Candles**: Historical daily OHLCV data from Finnhub for your watchlist
2. **Real Company News**: Fetch and analyze actual headlines from news feeds
3. **Real SEC Filings**: 10-K, 10-Q, 8-K events linked to market windows
4. **Real Sentiment**: NLP-based sentiment scoring on actual news
5. **Scheduled Ingestion**: Automated data sync (market hourly, news daily, filings weekly)
6. **Event Windows**: Real financial events tied to market anomaly analysis
7. **New API Endpoints**: `/ingestion/sync/*`, `/market-data/`, `/news/`, `/filings/`, etc.

---

## Features

| Module | What it does |
|--------|----------------|
| **Real market dashboard** | KPIs from real prices, real news feed, real event calendar |
| **Trade anomaly engine** | Rule heuristics + Isolation Forest on real market features |
| **Real news sentiment** | VADER + finance-aware tone analysis on actual headlines |
| **Social intelligence** | Coordinated hype bursts, bot-like posting patterns (synthetic simulation) |
| **Pump-and-dump prediction** | Multi-signal early warning using real volume + news context |
| **Insider graph** | NetworkX analytics + React Flow network explorer (simulated entity layer) |
| **Risk fusion** | Unified stock/trader score with natural-language explanations |
| **Alert queue** | Severity, confidence, status workflow (new → escalated → resolved) |
| **Heatmaps** | Sector, stock, event-window, real sentiment, social coordination |
| **Data ingestion** | Scheduled sync from Finnhub, SEC EDGAR, optional Polygon/Alpha Vantage |

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy, scikit-learn, NetworkX, VADER |
| Data Providers | Finnhub, SEC EDGAR API, optional Polygon.io, Alpha Vantage, GDELT |
| Ingestion | APScheduler, httpx, async pipelines |
| Database | **SQLite** (default, no install) · PostgreSQL (optional) |
| Frontend | React, Vite, Tailwind CSS, Recharts, React Flow |
| Tooling | pytest, Docker Compose (optional) |

---

## Prerequisites

- **Python 3.12+** — [python.org](https://www.python.org/downloads/) or Microsoft Store
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Docker Desktop** — optional only; not required for local run
- **API Keys** (optional for real-data mode):
  - [Finnhub](https://finnhub.io) — Free tier available (~60 req/min)
  - SEC EDGAR — No key needed (public API)
  - [Polygon.io](https://polygon.io) — Optional for real-time
  - [Alpha Vantage](https://www.alphavantage.co) — Optional fallback

---

## 📋 Step-by-Step Installation Guide (Windows)

Follow these 14 steps to get MarketShield AI running locally. **You will need 3 PowerShell terminals.**

### **Prerequisites Check**

**Step 1:** Verify Python is installed and version 3.12+
```powershell
python --version
```
Expected output: `Python 3.12.x` or higher

**Step 2:** Verify Node.js and npm are installed
```powershell
node --version
npm --version
```
Expected output: Node 18+ and npm 9+

If either is missing, install from [python.org](https://www.python.org/downloads/) and [nodejs.org](https://nodejs.org/)

---

### **Backend Setup (Terminal 1)**

**Step 3:** Navigate to the backend directory
```powershell
cd c:\Users\arvin\Downloads\Codeathon_cursor\marketshield-ai\backend
```

**Step 4:** Create a Python virtual environment
```powershell
python -m venv .venv
```
⏳ This creates a `.venv` folder (takes ~30 seconds)

**Step 5:** Activate the virtual environment

**Option A (Recommended for Windows):**
```powershell
.venv\Scripts\activate.bat
```

**Option B (If .bat fails):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.venv\Scripts\activate
```

✅ **Expected:** Your prompt should now show `(.venv)` at the beginning

Example:
```powershell
(.venv) PS C:\Users\arvin\Downloads\Codeathon_cursor\marketshield-ai\backend>
```

**Step 6:** Install Python dependencies
```powershell
pip install -r requirements.txt
```
⏳ This takes ~2-3 minutes. Wait for `Successfully installed...`

**Step 7:** Start the backend API server
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

✅ **Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

**Step 8:** Verify the backend is running
- Open your browser and go to: **http://localhost:8001/docs**
- You should see Swagger API documentation
- ✅ Keep this terminal open

---

### **Frontend Setup (Terminal 2 — New PowerShell)**

**Step 9:** Open a **new PowerShell terminal** and navigate to frontend
```powershell
cd c:\Users\arvin\Downloads\Codeathon_cursor\marketshield-ai\frontend
```

**Step 10:** Set the backend API URL environment variable
```powershell
$env:VITE_API_URL="http://localhost:8001"
```

**Step 11:** Install npm packages

**Use .cmd version (recommended for Windows):**
```powershell
npm.cmd install
```

If you get a PowerShell script execution error, this `.cmd` version bypasses it automatically.

✅ **Expected:** Ends with `added X packages`

**Step 12:** Start the frontend development server
```powershell
npm.cmd run dev
```

✅ **Expected output:**
```
Local:        http://localhost:5173
```

**Step 13:** Open the application in your browser
- Navigate to: **http://localhost:5173**
- You should see the MarketShield AI dashboard
- ✅ Keep this terminal open

---

### **Load Demo Data (Terminal 3 — New PowerShell)**

**Step 14:** Generate synthetic demo data (optional but recommended for first run)

Open a **third PowerShell terminal** (Terminal 1 and 2 should still be running) and run:

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/seed/generate-demo-data" -Method POST -ContentType "application/json" -Body '{"days": 30}'
```

✅ **Expected output:**
```
status  : success
message : Demo data generated successfully
```

Then refresh your browser at **http://localhost:5173** to see the dashboard populated with data.

---

### **First Launch Verification Checklist**

| ✓ | Step | Verification |
|---|------|--------------|
| [ ] | Step 1-2 | Python 3.12+ and Node 18+ installed |
| [ ] | Step 7 | Backend running at http://localhost:8001/docs |
| [ ] | Step 12 | Frontend running at http://localhost:5173 |
| [ ] | Step 14 | Demo data generated successfully |
| [ ] | Dashboard | See KPIs, charts, and alert data |

---

### **Quick Troubleshooting During Setup**

| Problem | Solution |
|---------|----------|
| **Step 5:** Script execution error | Use `.venv\Scripts\activate.bat` instead |
| **Step 11:** npm script error | Use `npm.cmd install` instead of `npm install` |
| **Step 12:** npm run dev fails | Use `npm.cmd run dev` instead of `npm run dev` |
| **Step 7:** Port 8001 already in use | Use `--port 8080` instead |
| **Step 13:** Dashboard is empty | Run Step 14 (generate demo data) |
| **Step 13:** Frontend can't reach API | Verify Terminal 1 is running and Step 10 was executed |

---

## Quick start (Windows — recommended)

**Follow the 14 steps in [Step-by-Step Installation Guide](#-step-by-step-installation-guide-windows) above.**

Default database is SQLite — no PostgreSQL or Docker needed. You'll need **3 PowerShell terminals**.

**TL;DR:**
1. Terminal 1: Backend — `python -m venv .venv` → `.venv\Scripts\activate.bat` → `pip install -r requirements.txt` → `python -m uvicorn app.main:app --reload --port 8001`
2. Terminal 2: Frontend — `npm.cmd install` → `npm.cmd run dev`
3. Terminal 3: Seed data — `Invoke-RestMethod -Uri "http://localhost:8001/api/v1/seed/generate-demo-data" -Method POST -ContentType "application/json" -Body '{"days": 30}'`

Then open **http://localhost:5173** in your browser.  

---

## Judge demo walkthrough (~5 min)

| Step | Page | What to show |
|------|------|----------------|
| 1 | **Dashboard** | KPI cards, anomaly chart, top risk tickers, alert feed |
| 2 | **Alerts** | Click an alert → explanation, drivers, escalate/dismiss |
| 3 | **Stocks → APEX** | Pump-and-dump prediction + social hype |
| 4 | **Stocks → HELIX** | Insider accumulation pre-earnings |
| 5 | **Insider Graph** | Suspicious clusters (red edges, insider links) |
| 6 | **Sentiment & Social** | APEX hype narrative |
| 7 | **Heatmaps** | Sector / stock risk grids |
| 8 | **Demo Control** | Explain 4 embedded scenarios to judges |

---

## Embedded demo scenarios

| Scenario | Ticker / traders | Signal |
|----------|------------------|--------|
| Insider buildup before earnings | HELIX · TR-001–003 | Pre-event accumulation + insider graph links |
| Pump-and-dump social hype | APEX · retail cluster | Social burst + volume/price spike |
| Coordinated trading cluster | QUANT · TR-005–007 | Shared device + synchronized buys |
| Spoof-like cancel pattern | NEXA · TR-008 | High cancel-to-fill ratio |

---

## URLs

| Service | URL |
|---------|-----|
| Surveillance UI | http://localhost:5173 |
| API (Swagger) | http://localhost:8001/docs |
| Health check | http://localhost:8001/api/v1/health |

Change `8001` if you used a different backend port — and set `VITE_API_URL` to match.

---

## Project structure

```
marketshield-ai/
├── backend/
│   ├── app/
│   │   ├── api/          REST routes
│   │   ├── ml/           Anomaly, sentiment, pump-dump, risk fusion
│   │   ├── graph/        Insider network (NetworkX)
│   │   ├── seed/         Synthetic data generator
│   │   ├── models/       SQLAlchemy entities
│   │   └── services/     Dashboard & insights
│   ├── data/             SQLite DB (created on first run)
│   └── tests/
├── frontend/
│   └── src/pages/        Dashboard, Alerts, Stocks, Graph, etc.
├── docker-compose.yml    Optional (requires Docker Desktop)
├── .env.example
└── README.md
```

---

## Configuration (`.env`)

Copy from `.env.example`:

```powershell
copy .env.example .env
```

**Default (SQLite — no extra setup):**

```env
DATABASE_URL=sqlite+aiosqlite:///./data/marketshield.db
DATABASE_URL_SYNC=sqlite:///./data/marketshield.db
VITE_API_URL=http://localhost:8001
```

**PostgreSQL (Docker or local Postgres):** uncomment the `postgresql://` lines in `.env.example` and use port `8000` or `8001` consistently.

---

## Real-Data Configuration

### Get Your API Keys

#### Finnhub (for market data & news)

1. Visit https://finnhub.io → Sign up (free)
2. Copy API key
3. Add to `.env`:

```bash
FINNHUB_API_KEY=your_finnhub_key_here
```

#### SEC EDGAR (for filings/events — no key needed)

Add your user agent to `.env`:

```bash
SEC_USER_AGENT=MarketShieldAI/1.0 your-email@example.com
```

#### Polygon.io (Optional — real-time streaming)

Add to `.env`:

```bash
POLYGON_API_KEY=your_polygon_key_here
```

#### Alpha Vantage (Optional — fallback data)

Add to `.env`:

```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

### Configure Watchlist & Ingestion

```bash
# Comma-separated tickers (real symbols only)
DEFAULT_WATCHLIST=AAPL,MSFT,NVDA,TSLA,AMZN

# Ingestion frequency (minutes)
MARKET_SYNC_INTERVAL=30
NEWS_SYNC_INTERVAL=60
FILINGS_SYNC_INTERVAL=1440

# Enable/disable
MARKET_SYNC_ENABLED=true
NEWS_SYNC_ENABLED=true
FILINGS_SYNC_ENABLED=true
```

### Test Real-Data Ingestion

After adding API keys and restarting backend:

```powershell
# Sync market data
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ingestion/sync/market" -Method POST

# Check status
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ingestion/status" -Method GET

# Query real data
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/market-data/AAPL?days=30" -Method GET
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/news/AAPL?limit=5" -Method GET
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/filings/AAPL" -Method GET
```

**Scheduler automatically syncs data** on the configured intervals — no manual action needed after startup.

---

## New Ingestion & Real-Data API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ingestion/sync/market` | POST | Fetch real OHLCV bars (Finnhub) |
| `/ingestion/sync/news` | POST | Fetch real news articles (Finnhub) |
| `/ingestion/sync/filings` | POST | Fetch real SEC filings (EDGAR) |
| `/ingestion/status` | GET | View ingestion run history |
| `/market-data/{symbol}` | GET | Query stored market bars |
| `/news/{symbol}` | GET | Query stored news articles |
| `/filings/{symbol}` | GET | Query stored SEC filings |

---

## Architecture: Hybrid Real + Synthetic

```
┌──────────────────────────────────────────┐
│     MarketShield AI (Real-Data Hybrid)   │
├──────────────────────────────────────────┤
│ ✅ REAL: Market bars, news, filings      │
│ ⚠️  HYBRID: Features, anomaly detection   │
│ 🔄 SYNTHETIC: Traders, entity graph      │
│ 📊 ANALYTICS: Unified risk scores        │
└──────────────────────────────────────────┘
```

---



## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | API + database status |
| POST | `/api/v1/seed/generate-demo-data` | Generate synthetic dataset |
| GET | `/api/v1/dashboard/overview` | Main dashboard payload |
| GET | `/api/v1/dashboard/market-heatmap` | Heatmap data |
| GET | `/api/v1/alerts` | Alert queue |
| PATCH | `/api/v1/alerts/{id}` | Update alert status |
| GET | `/api/v1/stocks/{ticker}/risk` | Unified risk score |
| GET | `/api/v1/stocks/{ticker}/pump-dump-prediction` | Pump-and-dump estimate |
| GET | `/api/v1/traders/{id}/graph` | Trader subgraph |
| GET | `/api/v1/graphs/insider-network` | Full insider network |
| GET | `/api/v1/demo/scenarios` | Demo walkthrough metadata |
| POST | `/api/v1/ml/retrain` | Refresh models on seeded data |
| WS | `/api/v1/stream/alerts` | Alert stream (WebSocket) |

Full interactive docs: http://localhost:8001/docs

---

## Docker (optional)

Requires **Docker Desktop** installed and `docker` available in PATH.

```powershell
cd marketshield-ai
copy .env.example .env
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000/docs |

Then seed via **Demo Control** in the UI or:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/seed/generate-demo-data" -Method POST -ContentType "application/json" -Body '{"days": 30}'
```

If `docker` is not recognized, use the [Windows quick start](#quick-start-windows--recommended) above instead.

---

## Tests

```powershell
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Troubleshooting (Windows)

| Problem | Fix |
|---------|-----|
| **PowerShell script execution error** (.venv\Scripts\activate) | Use `.venv\Scripts\activate.bat` instead, or run `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process` |
| **npm script execution error** | Use `npm.cmd install` and `npm.cmd run dev` instead of `npm` and `npm run dev` |
| `docker` not recognized | Docker not installed — use local SQLite setup (this README's quick start) |
| `uvicorn` not recognized | Use `python -m uvicorn app.main:app --reload --port 8001` |
| `WinError 10013` on port 8000 | Port blocked — use **8001** and set `$env:VITE_API_URL="http://localhost:8001"` |
| Seed returns **Internal Server Error** | Restart backend after pulling latest code; ensure Terminal 1 is running |
| Empty dashboard | Run seed again or use **Demo Control → Generate demo data** |
| Frontend can't reach API | Set `$env:VITE_API_URL` to your backend URL before `npm.cmd run dev` |
| `ModuleNotFoundError` in backend | Verify `.venv\Scripts\activate.bat` was run and pip install completed |
| `gradio` / `multipart` pip warning | Use project `.venv` — avoids global package conflicts |

---

## Screenshots (for submission)

Add captures under `docs/screenshots/`:

- `dashboard.png` — surveillance dashboard
- `alerts.png` — alert queue with explainability
- `graph.png` — insider network explorer
- `demo.png` — demo control panel

---

## Future scope

- Real market data adapters (licensed feeds)
- SHAP explainability for ML outputs
- Celery / Redis streaming ingestion
- Case management RBAC and audit trail
- Regulatory export (SAR-style templates)

---

## Team / hackathon notes

- Built for **national-level hackathon** demonstration: synthetic data only, production-style architecture.
- Designed for judges evaluating **innovation**, **explainability**, **UX**, and **technical depth**.
- All advanced modules (graph, sentiment, pump-dump, fusion) have working baseline implementations — not placeholders.

---

## License & disclaimer

This project is a **demonstration surveillance platform**. Do not use outputs as evidence of illegal activity without formal investigation. Not financial advice.
