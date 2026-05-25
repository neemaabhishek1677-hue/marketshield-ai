# MarketShield AI

**AI-Based Market Manipulation & Insider Trading Detection Platform**

A hackathon-grade market surveillance workstation that detects trade anomalies, sentiment-driven manipulation, pump-and-dump risk, and insider-linked trading clusters — with explainable alerts and interactive investigation views.

> **Disclaimer:** All data is **synthetic**. Outputs are surveillance signals for demo and compliance-style review — **not** legal conclusions or investment advice.

---

## Features

| Module | What it does |
|--------|----------------|
| Market dashboard | KPIs, anomaly timeline, sector risk, alert feed, pump watchlist |
| Trade anomaly engine | Rule heuristics + Isolation Forest with feature drivers |
| News sentiment | VADER + hype / misinformation tone scoring |
| Social intelligence | Coordinated hype bursts, bot-like posting patterns |
| Pump-and-dump prediction | Multi-signal early warning per ticker |
| Insider graph | NetworkX analytics + React Flow network explorer |
| Risk fusion | Unified stock/trader score with natural-language explanations |
| Alert queue | Severity, confidence, status workflow (new → escalated → resolved) |
| Heatmaps | Sector, stock, event-window, sentiment, social coordination |
| Demo control | One-click seed + 4 judge-ready walkthrough scenarios |

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy, scikit-learn, NetworkX, VADER |
| Database | **SQLite** (default, no install) · PostgreSQL (optional, Docker) |
| Frontend | React, Vite, Tailwind CSS, Recharts, React Flow |
| Tooling | pytest, Docker Compose (optional) |

---

## Prerequisites

- **Python 3.12+** — [python.org](https://www.python.org/downloads/) or Microsoft Store
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Docker Desktop** — optional only; not required for local run

---

## Quick start (Windows — recommended)

Use **3 terminals**. Default database is SQLite — no PostgreSQL or Docker needed.

### Terminal 1 — Backend API

```powershell
cd c:\Users\arvin\Downloads\Codeathon_cursor\marketshield-ai
copy .env.example .env

cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

> **Port note:** If port `8000` fails with `WinError 10013`, use **8001** (or 8080) as shown above.

Wait until you see:

```text
Uvicorn running on http://127.0.0.1:8001
```

Verify: http://localhost:8001/docs

---

### Terminal 2 — Seed demo data

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/seed/generate-demo-data" -Method POST -ContentType "application/json" -Body '{"days": 30}'
```

**Success response** includes roughly:

- `stocks: 8`
- `traders: 40`
- `trades: 785`
- `alerts: 4`

---

### Terminal 3 — Frontend UI

```powershell
cd c:\Users\arvin\Downloads\Codeathon_cursor\marketshield-ai\frontend
$env:VITE_API_URL="http://localhost:8001"
npm.cmd install
npm.cmd run dev
```

> **PowerShell script error?** If `npm run dev` says scripts are disabled, use **`npm.cmd`** instead of `npm` (see [Troubleshooting](#troubleshooting-windows)).

Open: **http://localhost:5173**

---

### First launch checklist

1. Backend running on **8001** ✓  
2. Seed command returned success ✓  
3. Frontend open at http://localhost:5173 ✓  
4. Go to **Demo Control** → **Generate demo data** (if dashboard is empty)  
5. Open **Dashboard** — confirm KPIs, charts, and alerts appear  

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
| `docker` not recognized | Docker not installed — use local SQLite setup (this README’s quick start) |
| `uvicorn` not recognized | Use `python -m uvicorn app.main:app --reload --port 8001` |
| `WinError 10013` on port 8000 | Port blocked — use **8001** and set `$env:VITE_API_URL="http://localhost:8001"` |
| `npm` / scripts disabled (PowerShell) | Use `npm.cmd install` and `npm.cmd run dev` |
| Seed returns **Internal Server Error** | Restart backend after pulling latest code; ensure Terminal 1 is running |
| Empty dashboard | Run seed again or use **Demo Control → Generate demo data** |
| Frontend can’t reach API | Set `$env:VITE_API_URL` to your backend URL before `npm.cmd run dev` |
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
