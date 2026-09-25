# API response contract

All JSON success responses use `{"success": true, "data": ...}`. Paginated
success responses place `count`, `next`, `previous`, and `results` inside
`data`. A successful `204 No Content` response intentionally has no body.

All handled errors use `{"success": false, "error": ...}`. An error includes
`code`, `message`, `details`, and the request's correlation ID. The response
also includes the same ID in `X-Request-ID`.

The request ID is generated when a client does not send one, or preserved from
a caller-provided `X-Request-ID`. It is safe to provide to support staff; do
not use it as authentication or authorization data.

The API exposes no internal stack traces, SQL, file paths, or credentials.
Domain services raise `BusinessRuleViolation` for state/business-rule failures,
which becomes a `BUSINESS_RULE_VIOLATION` error with HTTP 400.
