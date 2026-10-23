from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

# Render terminates TLS at its edge and forwards the original scheme in this
# header. Django needs it to recognize HTTPS and avoid redirect loops.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

render_hostname = env("RENDER_EXTERNAL_HOSTNAME", default="").strip()
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, render_hostname]

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="None")
JWT_COOKIE_SECURE = True
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", default="None")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
# Turn these on only after all subdomains are HTTPS and you control the domain.
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

if STORAGE_BACKEND != "supabase":
    raise ImproperlyConfigured(
        "Production requires STORAGE_BACKEND=supabase; Render's filesystem "
        "is ephemeral."
    )
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ImproperlyConfigured(
        "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required in production."
    )
if not CORS_ALLOWED_ORIGINS or not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        "Set CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS to the deployed "
        "frontend origin(s)."
    )
if not FRONTEND_BASE_URL.startswith("https://"):
    raise ImproperlyConfigured("Production FRONTEND_BASE_URL must be an HTTPS URL.")
if not RESEND_API_KEY or not RESEND_FROM_EMAIL:
    raise ImproperlyConfigured(
        "RESEND_API_KEY and RESEND_FROM_EMAIL are required in production."
    )

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "infrastructure.logging.formatters.JsonFormatter"},
    },
    "filters": {
        "request_id": {"()": "infrastructure.logging.filters.RequestIDFilter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_id"],
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "infrastructure": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
