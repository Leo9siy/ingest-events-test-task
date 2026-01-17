# Ingest Events & Analytics Service

Small service to ingest product events and provide basic analytics (DAU, top events, retention).

## Features
- **POST /events** accepts a JSON array of events:
  - `event_id` (UUID)
  - `occurred_at` (ISO-8601)
  - `user_id` (string)
  - `event_type` (string)
  - `properties` (json object)
- **Idempotency**: repeated event with the same `event_id` is ignored (no duplicates)
- Analytics:
  - `GET /stats/dau?from=YYYY-MM-DD&to=YYYY-MM-DD` — unique users per day
  - `GET /stats/top-events?from=YYYY-MM-DD&to=YYYY-MM-DD&limit=10` — top `event_type` by count
  - `GET /stats/retention?start_date=YYYY-MM-DD&windows=3` — cohort retention (daily/weekly, see below)
- CLI import:
  - `import_events <path-to-csv>`
- Observability:
  - structured logs
  - basic metrics (request latency, ingested events count)
- Basic stability:
  - request validation
  - in-memory rate limiting (token bucket)

---

## Tech Stack
- FastAPI
- SQLAlchemy (async) + asyncpg
- PostgreSQL
- pytest + httpx (ASGITransport)

---

## Quickstart (Docker)
### 1) Start services
```bash
docker-compose up --build
