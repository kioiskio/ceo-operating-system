# CEO Operating System (Web)

A web app for founder operating decisions: run the numbers with deterministic tools, then optionally send the results to your own LLM for a written analysis. No accounts, no cloud — everything runs locally and your LLM key stays in your browser.

Author: kioiskio

## Features

- **SaaS Health Check** — 8 core metrics (ARR, growth, churn, NRR, CAC payback, gross margin, burn, cash) → GREEN / AMBER / RED ratings per metric, cash runway, and a 0–100 health score with recommendations.
- **Equity Dilution Simulator** — model multiple funding rounds (amount, pre-money, option pool expansion) → per-round cap table, ownership charts, and a founder dilution summary.
- **Pitch Deck Scorer** — a weighted 10-slide checklist distilled from funded decks → readiness verdict (READY / NEEDS WORK / NOT READY), per-slide breakdown, priority fixes, and JSON export.
- **AI Deep Analysis** — every tool result can be sent to a user-configured LLM (any OpenAI-compatible endpoint: OpenAI, OpenRouter, DeepSeek, local models, …) for a written advisor analysis. The backend only proxies the request; your API key is stored in browser localStorage and never persisted on the server.
- **Frameworks** — the fundraising decision tree (rendered diagram) and the PMF framework as built-in reading.
- **Templates** — pitch deck outline and 1:1 agenda, ready to copy or download.
- **Run History** — every run is saved locally (SQLite) and can be revisited or deleted.
- **Light / Dark theme** — follows your system by default, switchable in the header.

*Decision support only — not legal, tax, or investment advice. Verify with counsel and accountants.*

## Getting Started

Prerequisites: Python 3.11+ and Node.js 20+.

```bash
# 1. Backend setup
cd web/backend
python -m venv .venv
source .venv/Scripts/activate        # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Build the frontend
cd ../frontend
npm install
npm run build

# 3. Run (serves the app and the API on one port)
cd ../backend
python -m app.main
```

Open **http://localhost:8000**.

### Development mode

```bash
cd web/backend && uvicorn app.main:app --reload --port 8000
cd web/frontend && npm run dev       # http://localhost:5173, /api proxied to :8000
```

### Tests

```bash
cd web/backend && pytest tests/ -v
```

### Configuring the LLM

Go to **Settings** in the app, fill in:

- **Base URL** — e.g. `https://api.openai.com/v1` or `https://openrouter.ai/api/v1`
- **API Key** — stored only in your browser
- **Model** — e.g. `gpt-4o-mini` or `deepseek/deepseek-chat`

Click **Test Connection** to verify, then use **AI Deep Analysis** on any tool result page.

## Project Layout

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry (API + static hosting of frontend/dist)
│   │   ├── domain/          # pure calculation logic (saas health / equity / deck scoring)
│   │   ├── api/             # tools, llm, history, content routers
│   │   ├── services/        # OpenAI-compatible LLM proxy (httpx)
│   │   ├── content/         # framework & template markdown
│   │   └── db.py            # SQLite run history (backend/data/runs.db)
│   └── tests/               # pytest
└── frontend/                # React 19 + TypeScript + Ant Design 5 + Tailwind 4 + recharts
```

API reference: `http://localhost:8000/api/docs` while the server is running.

## License

MIT
