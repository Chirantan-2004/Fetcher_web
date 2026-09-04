# Fetcher

Fetcher turns accessible web pages into clean, structured records and professional JSON, DOCX, and PDF files.

## Run locally

1. Create a virtual environment and install `backend/requirements.txt`.
2. Copy `.env.example` to `.env`.
3. Start the API: `set PYTHONPATH=backend && uvicorn app.main:app --reload --app-dir backend`.
4. Install frontend dependencies in `frontend` with `npm install`, then run `npm run dev`.

The dashboard is available at http://localhost:5173 and the API at http://localhost:8000/docs.

## Docker

Copy `.env.example` to `.env`, then run `docker compose up --build`.

## API

- `POST /api/v1/fetch` queues one URL.
- `POST /api/v1/fetch/batch` queues up to ten URLs.
- `GET /api/v1/jobs/{job_id}` returns progress.
- `GET /api/v1/jobs/{job_id}/result` returns the versioned canonical JSON.
- `GET /api/v1/jobs/{job_id}/files` lists generated files.
- `GET /api/v1/jobs/{job_id}/files/{json|docx|pdf}` downloads a file.
- `GET /api/v1/health` returns service health.

## Design

HTTP retrieval is SSRF-aware and bounded by timeout and response size. Extraction removes common UI noise and preserves semantic sections, lists, tables, links, and metadata. DOCX and PDF are generated from the same canonical Pydantic model. Local storage and SQLite are defaults; the storage and database boundaries are ready for PostgreSQL and object storage adapters.

## Tests

From the repository root: `set PYTHONPATH=backend && pytest backend/tests`.

## Limitations

The current worker uses FastAPI background tasks, so durable distributed queues, browser rendering, robots policy enforcement, and rate limiting should be added before high-volume deployment. It does not bypass authentication, paywalls, CAPTCHA, or anti-bot controls.
