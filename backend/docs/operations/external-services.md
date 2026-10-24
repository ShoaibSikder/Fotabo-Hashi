# External service configuration

The backend keeps provider credentials in `backend/.env`; never put server
secrets in frontend environment variables. `.env.example` contains variable
names and placeholders only.

## Supabase PostgreSQL

Set `DATABASE_URL` to the project's PostgreSQL connection URI. Copy the URI
from Supabase's Connect panel; shared pooler URIs use the project-scoped user
`postgres.<project-ref>`. Include `sslmode=require` and percent-encode reserved
characters in the password. The settings parser can add the project ref when
the shared-pooler URI has the default `postgres` user. `DB_CONN_MAX_AGE`
controls Django's persistent connection lifetime (60 seconds by default).
`DATABASE_URL` is required; there is no local PostgreSQL fallback.

Use a dedicated application database role with only the privileges Fotabo Hashi
needs; do not use a Supabase superuser for normal application traffic because
PostgreSQL superusers bypass row-level security.

## Supabase Storage

Set `STORAGE_BACKEND=supabase`, `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_STORAGE_BUCKET` after creating the
bucket. The service-role key bypasses Storage RLS and must remain backend-only.
Active-member photos are stored at random object paths under
`founding-members/`. Django creates signed read URLs, so the bucket may remain
private. `SUPABASE_SIGNED_URL_TTL` controls their lifetime (3600 seconds by
default). Keep `STORAGE_BACKEND=local` while developing without Supabase
credentials.

## Resend password-reset email

Set `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, and `FRONTEND_BASE_URL`. Production
mail must come from a sender domain verified in Resend; the Resend-provided
`resend.dev` sender is for testing. Reset URLs use Django's expiring,
single-use password-reset token and point to the frontend's
`/reset-password?uid=...&token=...` route. The request endpoint reports an
unknown Fotabo Hashi account as not found, as requested; this allows account
enumeration, so the endpoint is rate-limited. Provider credentials and reset
tokens are never returned by the API. During local development, leaving the
Resend key blank sends reset email to Django's console backend instead.

Other environment values are grouped by purpose in `.env.example`: Django
security, CORS/CSRF origins, upload limits, Redis/cache, Celery, JWT cookie
settings, error monitoring, and PostgreSQL backup configuration. Keep
production values in the deployment platform's secret manager rather than
committing them.
