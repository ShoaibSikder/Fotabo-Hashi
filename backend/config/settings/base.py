from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import environ
import sentry_sdk
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
    "rest_framework_simplejwt.token_blacklist",
    "apps.common",
    "apps.accounts",
    "apps.profiles",
    "apps.donors",
    "apps.blood_requests",
    "apps.leaderboard",
    "apps.content",
    "apps.administration",
    "apps.audit",
    "apps.notifications",
]

MIDDLEWARE = [
    "apps.common.middleware.request_id.RequestIDMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "infrastructure.database.rls.middleware.ClearRLSContextMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "accounts.User"

SUPABASE_URL = env("SUPABASE_URL", default="")
DATABASE_URL = env("DATABASE_URL", default="").strip()
DB_CONN_MAX_AGE = env.int("DB_CONN_MAX_AGE", default=60)


def database_from_url(database_url):
    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname:
        raise ImproperlyConfigured(
            "DATABASE_URL must be a valid postgres:// or postgresql:// URL."
        )

    query = parse_qs(parsed.query)
    sslmode = (query.get("sslmode") or [None])[0]
    options = {"sslmode": sslmode or ("require" if not DEBUG else "prefer")}
    database_user = unquote(parsed.username or "")
    if database_user == "postgres" and parsed.hostname.endswith(".pooler.supabase.com"):
        project_host = urlparse(SUPABASE_URL).hostname or ""
        if project_host.endswith(".supabase.co"):
            project_ref = project_host.removesuffix(".supabase.co")
            if project_ref and "." not in project_ref:
                database_user = f"postgres.{project_ref}"
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": database_user,
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname,
        "PORT": str(parsed.port or 5432),
        "OPTIONS": options,
        "CONN_MAX_AGE": DB_CONN_MAX_AGE,
    }


if not DATABASE_URL:
    raise ImproperlyConfigured(
        "DATABASE_URL is required. Configure the Supabase PostgreSQL "
        "connection string in backend/.env."
    )

DATABASES = {"default": database_from_url(DATABASE_URL)}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.smtp.EmailBackend"
    ),
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@fotabohashi.org")
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:5173")
RESEND_API_KEY = env("RESEND_API_KEY", default="")
RESEND_FROM_EMAIL = env("RESEND_FROM_EMAIL", default="") or DEFAULT_FROM_EMAIL
RESEND_TIMEOUT_SECONDS = env.int("RESEND_TIMEOUT_SECONDS", default=15)

JWT_ACCESS_COOKIE_NAME = env("JWT_ACCESS_COOKIE_NAME", default="fh_access")
JWT_REFRESH_COOKIE_NAME = env("JWT_REFRESH_COOKIE_NAME", default="fh_refresh")
JWT_COOKIE_SECURE = env.bool("JWT_COOKIE_SECURE", default=False)
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", default="Lax")
SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="development")
SENTRY_TRACES_SAMPLE_RATE = env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        send_default_pii=False,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
    )
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "fotabo_hashi",
        "TIMEOUT": 300,
    },
}
MAX_UPLOAD_SIZE_MB = env.int("MAX_UPLOAD_SIZE_MB", default=5)
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int(
    "FILE_UPLOAD_MAX_MEMORY_SIZE",
    default=MAX_UPLOAD_SIZE_MB * 1024 * 1024,
)
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int(
    "DATA_UPLOAD_MAX_MEMORY_SIZE",
    default=10 * 1024 * 1024,
)

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGE_BACKEND = env("STORAGE_BACKEND", default="local").lower()
SUPABASE_SERVICE_ROLE_KEY = env("SUPABASE_SERVICE_ROLE_KEY", default="")
SUPABASE_STORAGE_BUCKET = env(
    "SUPABASE_STORAGE_BUCKET",
    default="fotabo-hashi-media",
)
SUPABASE_SIGNED_URL_TTL = env.int("SUPABASE_SIGNED_URL_TTL", default=3600)
STORAGES = {
    "default": {
        "BACKEND": (
            "infrastructure.storage.backends.LocalMediaStorage"
            if STORAGE_BACKEND == "local"
            else "infrastructure.storage.backends.SupabaseStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "apps.common.renderers.StandardJSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.CookieOrBearerJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": ("apps.common.pagination.StandardPagination"),
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.common.throttles.CacheFailOpenAnonRateThrottle",
        "apps.common.throttles.CacheFailOpenUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "login": "10/minute",
        "refresh": "30/minute",
        "registration": "5/hour",
        "password_reset": "5/hour",
        "password_change": "5/hour",
        "blood_request_create": "30/hour",
        "blood_request_action": "60/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "EXCEPTION_HANDLER": ("apps.common.exceptions.handlers.api_exception_handler"),
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Fotabo Hashi API",
    "DESCRIPTION": "REST API for the Fotabo Hashi blood donation and donor discovery platform.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {
        "BloodRequestStatusEnum": "apps.blood_requests.models.BloodRequestStatus",
        "DonationCountReviewStatusEnum": [
            ("PENDING", "Pending"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("SUPERSEDED", "Superseded"),
        ],
    },
    "TAGS": [
        {"name": "Health", "description": "API health and service status."},
        {
            "name": "Authentication",
            "description": "Authentication and account endpoints.",
        },
        {"name": "Profile", "description": "Authenticated user profile operations."},
        {"name": "Donors", "description": "Privacy-safe donor discovery."},
        {"name": "Blood Requests", "description": "Blood request management."},
        {
            "name": "Leaderboard",
            "description": "Ranks active members by administrator-verified donations.",
        },
        {"name": "Public Content", "description": "Public organization content."},
        {
            "name": "Administration",
            "description": "User, request, and audit oversight for administrators.",
        },
        {
            "name": "Notifications",
            "description": "Private notifications for the signed-in user.",
        },
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}
