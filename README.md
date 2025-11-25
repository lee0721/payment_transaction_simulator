# 💳 Payment Transaction Simulator

Simulates a simplified payment-network authorization workflow using FastAPI, SQLite, and Docker. The service accepts payment requests, performs a fraud heuristic, persists the outcome, and exposes rich query and statistics endpoints.

> Built to showcase REST API design, SQL/ORM usage, fraud detection logic, Dockerization, and documentation polish for modern payment platforms.

---

## 🚀 Features
- **POST `/payment`** – Submit a simulated payment, run a fraud check, and receive an approval decision.
- **GET `/transaction/{id}`** – Retrieve full transaction details, including masked card information.
- **GET `/stats`** – Observe live metrics: totals, approval ratio, average ticket size, and P95 scoring latency.
- **GET `/audit/{transaction_id}`** – Inspect structured audit logs produced by the scoring & logging services.
- **Docker Compose stack** – Bring up FastAPI API, Postgres, Redis, worker, and the React demo with one command (healthchecks + seed helpers included).
- Randomized fraud logic with amount-aware thresholds.
- Auto-generated Swagger UI (`/docs`) & ReDoc (`/redoc`).
- Modern React/Vite UI at `/demo` (served from `frontend-app/dist` when available) with shared DTOs.
- `/admin/reset` endpoint (returns zeroed stats) with UI button for instant demo resets.
- SQLite persistence via SQLAlchemy; easy to swap for Postgres/Mongo.
- Docker-ready deployment for reproducible demos.

---

## 🛠️ Tech Stack
- Python 3.11 + FastAPI
- SQLAlchemy ORM + SQLite
- Uvicorn ASGI server
- Docker (optional but recommended)
- Pydantic data validation

---

## 🧭 Architecture at a Glance
```
Client (Demo UI / Swagger / curl)
        |
        v
  FastAPI Application (app/main.py)
   ├─ Schemas (app/schemas.py)      # Request/response validation
   ├─ Models  (app/models.py)       # SQLAlchemy ORM entities
   ├─ Database (app/database.py)    # SQLite engine & sessions
   ├─ Utils   (app/utils.py)        # Fraud heuristic & stats
  └─ React Demo (frontend-app/dist)# Built Vite bundle auto-served at /demo when present
        |
        v
      SQLite (transactions.db)
```

### New Service Modules
- `app/services/scoring.py` – wraps heuristics, cached features, and risk metadata.
- `app/services/audit.py` – writes decision logs and exposes `/audit/{transaction_id}`.
- `app/services/cache.py` – Redis-aware cache with graceful in-memory fallback.
- `worker/` – reusable tasks (synthetic seeding, feature refresh) plus `run_worker.py` for RQ workers.
- `shared/dtos/` – FastAPI OpenAPI export lives here so the React frontend can derive consistent DTOs.

---

## ▶️ Quick Start

```bash
git clone https://github.com/<your-username>/payment_transaction_simulator.git
cd payment_transaction_simulator
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Now open http://127.0.0.1:8000/docs for interactive Swagger UI.  
Need the full React demo while running only FastAPI? From `frontend-app/` run `npm install && npm run build` once and hit http://127.0.0.1:8000/demo, or launch the Vite dev server (`npm run dev`) and browse http://127.0.0.1:5173.

> 💡 If your shell cannot find `python`/`uvicorn`, invoke the binaries directly via `./.venv/bin/python -m uvicorn app.main:app --reload`.
> 📦 Planning to use Docker Compose? Copy `.env.example` to `.env` first so every service shares the same credentials.
> 🎨 Running via Docker Compose automatically serves the React UI at http://localhost:4173 (nginx). Without Docker, bundle once via `npm run build` so FastAPI can mount `/demo`.

---

## 🐳 Docker Workflow

### Single-container build
```bash
docker build -t payment-transaction-simulator .
docker run -p 8080:8080 payment-transaction-simulator
```

Visit http://127.0.0.1:8080/docs to explore the API or http://127.0.0.1:8080/demo for the bundled React demo (ensure `frontend-app/dist` exists before building).

### Full stack via Docker Compose
```bash
cp .env.example .env            # adjust secrets/ports as needed
make up                         # builds api + worker + frontend + postgres + redis
make logs                       # tail everything
make seed                       # optional: populate demo transactions
make down                       # teardown
```

- API available at `http://localhost:${API_PORT}` (defaults to 8000) with healthcheck at `/health`.
- React demo served from `http://localhost:${FRONTEND_PORT}` (defaults to 4173). FastAPI also exposes the same bundle at `/demo` whenever `frontend-app/dist` exists.
- Postgres + Redis are internal services; credentials configurable via `.env`.
- The `seed` target runs `scripts/seed_demo_data.py` inside the stack (profile `tools`), so you can quickly rehydrate the database.
- Run `make help` to list all helper commands.

---

## 🛰️ Background Worker (RQ) & Feature Cache
1. Ensure Redis is available (local or via Docker).
2. Install Python dependencies (`pip install -r requirements.txt`).
3. Launch the worker:
   ```bash
   PYTHONPATH=. REDIS_URL=redis://localhost:6379/0 python -m worker.run_worker
   ```
4. Enqueue tasks (e.g., from a Python shell) to seed transactions or refresh feature caches:
   ```python
   from rq import Queue
   from redis import Redis
   from worker import tasks

   q = Queue("riskops", connection=Redis.from_url("redis://localhost:6379/0"))
   q.enqueue(tasks.seed_synthetic_transactions, batch_size=25)
   ```
- You can also run `python scripts/seed_demo_data.py --batch-size 20` (or `make seed` when using Docker Compose) to quickly populate demo data.

---

## 🎨 React/Vite Frontend (`frontend-app/`)
- Modern demo UI sharing DTOs with the backend.
- Commands:
  ```bash
  cd frontend-app
  npm install
  npm run generate:dto  # copies shared/dtos/openapi.json into src/generated
  npm run dev           # http://localhost:5173 (uses Vite dev server)
  npm run build         # produce dist/ so FastAPI can serve /demo without docker-compose
  ```
- When Docker Compose is running, visit http://localhost:4173 to use the nginx-hosted build. Otherwise set `VITE_API_BASE` (e.g., `VITE_API_BASE=http://localhost:8000 npm run build`) to point the UI at the correct API.

---

## 🖥️ Visual Demo Walkthrough
![Interactive Demo](assets/demo.gif)

- **Submit Payment** – form-driven experience that populates the API request and surfaces the JSON result inline.
- **Inspect Transaction** – auto-fills the most recent transaction ID for quick lookups.
- **Monitor Stats** – pulls live aggregates to underline observability and support readiness.
- **Audit Trail** – new panel shows `/audit/{transaction_id}` output for transparency.
- Crafted with React + Vite for componentized UX, theming, and fast iteration.
- One-click "Clear Demo Data" control wired to `/admin/reset` for testing or presentation resets.

---

## 📡 API Reference

### POST `/payment`
Create a transaction and receive the authorization decision.

**Request**
```json
{
  "card_number": "4000001234567890",
  "amount": 150.75,
  "currency": "GBP",
  "merchant": "Amazon",
  "channel": "ecommerce",
  "device_id": "ios-demo-device"
}
```

**Successful Response – 201**
```json
{
  "transaction_id": "f8a7e1bc-45ff-42f9-81a5-3ac8b1459b33",
  "status": "Approved",
  "decision_reason": null,
  "score": 0.12,
  "latency_ms": 24.5,
  "features": {
    "spending_velocity": 0.31,
    "device_trust_score": 0.87,
    "ip_risk_score": 0.44
  }
}
```

Errors: `400` (validation failure), `500` (unexpected).

---

### GET `/transaction/{id}`
Retrieve the persisted transaction by ID (last 4 PAN digits only).

**Response – 200**
```json
{
  "id": "f8a7e1bc-45ff-42f9-81a5-3ac8b1459b33",
  "card_last4": "7890",
  "amount": 150.75,
  "currency": "GBP",
  "merchant": "Amazon",
  "channel": "ecommerce",
  "device_id": "ios-demo-device",
  "status": "Approved",
  "risk_flag": null,
  "created_at": "2025-10-21T12:34:56.123456"
}
```

Errors: `404` if not found.

---

### GET `/stats`
Aggregate view over all transactions.

**Response – 200**
```json
{
  "total": 128,
  "approved": 103,
  "declined": 25,
  "approval_rate": 0.8047,
  "avg_amount": 172.33,
  "p95_latency": 48.12
}
```

---

## 🔍 Fraud & Authorization Logic
- Amount > £500 → 30% probability of decline (`risk_flag: "High amount flagged..."`).
- Amount ≤ £500 → 90% probability of approval (10% randomized decline).
- Easy to extend with merchant blacklists, velocity checks, or ML hooks.

---

## 🗃️ Data Model (SQLite)

| Field        | Type    | Notes                                        |
|--------------|---------|----------------------------------------------|
| `id`         | UUID    | Primary key                                  |
| `card_number`| TEXT    | Stored in cleartext for demo, mask on output |
| `amount`     | REAL    | Transaction amount                           |
| `currency`   | TEXT    | ISO 4217 currency code                       |
| `merchant`   | TEXT    | Merchant descriptor                          |
| `channel`    | TEXT    | ecommerce / in-store / etc. (nullable)       |
| `device_id`  | TEXT    | Device fingerprint (nullable)                |
| `status`     | TEXT    | `Approved` / `Declined`                      |
| `risk_flag`  | TEXT    | Optional fraud reason                        |
| `created_at` | DATETIME| UTC timestamp                                |

> ⚠️ Demo only — real systems must tokenize PANs and comply with PCI-DSS.

---

## 🧪 Manual Testing Cheat Sheet

```bash
# Create a transaction
curl -X POST http://127.0.0.1:8000/payment \
  -H "Content-Type: application/json" \
  -d '{"card_number":"4000001234567890","amount":650.00,"currency":"GBP","merchant":"BestBuy","channel":"in-store","device_id":"ios-123"}'

# Query by ID (replace <id>)
curl http://127.0.0.1:8000/transaction/<transaction_id>

# View stats
curl http://127.0.0.1:8000/stats

# Reset demo state
curl -X DELETE http://127.0.0.1:8000/admin/reset
```

---

## 📊 Industry Alignment Highlights
- **Single development lifecycle** – Covers design, build, validation, documentation, and containerization.
- **Tech coverage** – Python, REST, SQL, Docker, Unix shell, data validation — core capabilities for payment-processing teams.
- **Support readiness** – `/stats` endpoint and clear logging hooks shorten time-to-debug.
- **Problem solving** – Fraud heuristic demonstrates risk thinking with pathways for future ML/analytics integration.
- **Collaboration-ready** – Modular app structure, well-documented API, and Docker workflow for seamless handoff.

---

## 🔄 CI/CD Automation
- `.github/workflows/ci.yml` runs linting (`ruff`), `pytest`, frontend build, `docker compose config`, and headless Playwright tests on every push/pull request.
- `Jenkinsfile` mirrors the same pipeline stages for self-hosted agents (Python lint/test → frontend build → compose validation → Playwright E2E).
- Both pipelines rely on Docker Compose to spin up the API/worker/Postgres/Redis/React stack end-to-end.

To execute locally:

```bash
docker compose up -d --build
npm install               # installs Playwright
E2E_BASE_URL=http://localhost:4173 npm run test:e2e
docker compose down -v
```

---

## 🌐 End-to-End Tests (Playwright)
- Playwright config lives in `playwright.config.ts`, tests under `tests/e2e/`.
- The default spec (`demo.spec.ts`) opens the React app, submits a transaction, verifies audit output, and checks live stats.
- Configure `E2E_BASE_URL` to aim at another host (e.g., staging) before running `npm run test:e2e`.
- `npm run test:e2e:headed` launches a visible browser for debugging.

---

## 🛣️ Future Enhancements
1. Add MongoDB-backed branch to showcase NoSQL skills.
2. Introduce background task for settlement/clearing simulation.
3. Instrument structured logging and request IDs for observability.
4. Wire GitHub Actions to run linting, tests, and Docker builds automatically.

---

## ✅ Verification Checklist
1. `docker compose up -d --build` launches API (8000), React UI (4173), worker, Postgres, and Redis. `make ps` shows all services healthy.
2. `curl -X POST http://localhost:8000/payment ...` returns a 201 decision payload, and `/transaction/{id}`, `/audit/{id}`, `/stats` all reflect the new row.
3. http://localhost:4173 (or `/demo`) lets you submit a payment, fetch the transaction, and refresh stats; DevTools → Network shows calls proxied to `http://localhost:8000/*`.
4. `docker compose down -v && docker compose up -d --build` resets the Postgres volume so newly added ORM fields (currency/channel/device_id) are reflected in the schema for clean demos.

---

## 📄 License
Released under the MIT License. See `LICENSE` for details.
