# 💳 Payment Transaction Simulator

Simulates a simplified payment-network authorization workflow using FastAPI, SQLite, and Docker. The service accepts payment requests, performs a fraud heuristic, persists the outcome, and exposes rich query and statistics endpoints.

> Built to showcase REST API design, SQL/ORM usage, fraud detection logic, Dockerization, and documentation polish for modern payment platforms.

---

## 🚀 Features
- **POST `/payment`** – Submit a simulated payment, run a fraud check, and receive an approval decision.
- **GET `/transaction/{id}`** – Retrieve full transaction details, including masked card information.
- **GET `/stats`** – Observe live metrics: totals, approval ratio, and average ticket size.
- Randomized fraud logic with amount-aware thresholds.
- Auto-generated Swagger UI (`/docs`) & ReDoc (`/redoc`).
- Dark-mode guided UI at `/demo` so non-technical reviewers can explore the workflow without curl.
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
   └─ Static Demo (frontend/)       # Dark-mode walkthrough for non-engineers
        |
        v
      SQLite (transactions.db)
```

---

## ▶️ Quick Start

```bash
git clone https://github.com/<your-username>/payment_transaction_simulator.git
cd payment_transaction_simulator
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Now open http://127.0.0.1:8000/docs for interactive Swagger UI, or http://127.0.0.1:8000/demo for the guided visual experience.

> 💡 If your shell cannot find `python`/`uvicorn`, invoke the binaries directly via `./.venv/bin/python -m uvicorn app.main:app --reload`.

---

## 🐳 Docker Workflow

```bash
docker build -t payment-transaction-simulator .
docker run -p 8080:8080 payment-transaction-simulator
```

Visit http://127.0.0.1:8080/docs to explore the API inside the container.

Or open http://127.0.0.1:8080/demo for the frontend walkthrough served from the same container.

---

## 🖥️ Visual Demo Walkthrough
![Interactive Demo](assets/demo.gif)

- **Submit Payment** – form-driven experience that populates the API request and surfaces the JSON result inline.
- **Inspect Transaction** – auto-fills the most recent transaction ID for quick lookups.
- **Monitor Stats** – pulls live aggregates to underline observability and support readiness.
- Crafted with vanilla JS + CSS to keep dependencies light while showcasing UI polish (dark theme, responsive layout).
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
  "merchant": "Amazon"
}
```

**Successful Response – 201**
```json
{
  "transaction_id": "f8a7e1bc-45ff-42f9-81a5-3ac8b1459b33",
  "status": "Approved"
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
  "merchant": "Amazon",
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
  "avg_amount": 172.33
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
| `merchant`   | TEXT    | Merchant descriptor                          |
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
  -d '{"card_number":"4000001234567890","amount":650.00,"merchant":"BestBuy"}'

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

## 🛣️ Future Enhancements
1. Add MongoDB-backed branch to showcase NoSQL skills.
2. Introduce background task for settlement/clearing simulation.
3. Instrument structured logging and request IDs for observability.
4. Wire GitHub Actions to run linting, tests, and Docker builds automatically.

---

## 📄 License
Released under the MIT License. See `LICENSE` for details.
