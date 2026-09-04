# API

All endpoints are under `/api/v1`. `POST /fetch` accepts `{ "url": "https://example.com" }` and returns a queued UUID. Poll `/jobs/{id}` until `completed`, then use `/result` or `/files/{kind}`. Errors use `{ "code", "message", "retryable" }` where applicable.
