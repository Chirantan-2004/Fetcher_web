# Development

Backend modules live under `backend/app`. Run `pytest backend/tests` with `PYTHONPATH=backend`. Frontend uses Vite and React. Keep the canonical schema as the contract between extraction and all output generators. Never add a fetch path that bypasses URL validation or response limits.
