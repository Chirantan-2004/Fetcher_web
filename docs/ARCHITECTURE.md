# Architecture

The API creates a job, then the processing service fetches a bounded HTTP response, parses it into a canonical Pydantic document, and sends that same model to JSON, DOCX, PDF, and storage adapters. SQLite is the local default and SQLAlchemy keeps the model PostgreSQL-ready. Background tasks are an intentionally replaceable execution boundary for Redis/Celery.
