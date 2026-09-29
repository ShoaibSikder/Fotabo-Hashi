# Monitoring and observability

`GET /api/v1/health/live/` is a public liveness probe. It only verifies that
the Django process can respond.

`GET /api/v1/health/ready/` verifies PostgreSQL, Redis, and the configured
storage backend. It returns `503` with generic dependency statuses when a
required dependency is unavailable. It never returns hostnames, credentials,
or exception text.

Production logs are JSON records that include safe request metadata such as a
request ID, HTTP method, path, and status code. Request bodies, cookies,
authorization headers, tokens, and credentials must never be logged.

Sentry is opt-in through `SENTRY_DSN`. It is initialized with
`send_default_pii=False`; production should set `SENTRY_ENVIRONMENT=production`.
