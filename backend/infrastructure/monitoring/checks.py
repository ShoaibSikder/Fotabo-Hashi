import logging

from django.db import connection

from infrastructure.cache.services import check_cache_connection
from infrastructure.storage.services import check_storage_connection

logger = logging.getLogger(__name__)


def _run_check(name, check):
    try:
        check()
    except Exception:
        logger.exception("Dependency health check failed", extra={"dependency": name})
        return {"status": "error"}
    return {"status": "ok"}


def check_database_connection():
    def query_database():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

    return _run_check("database", query_database)


def check_redis_connection():
    return _run_check("redis", lambda: _require_true(check_cache_connection()))


def check_storage():
    return _run_check("storage", lambda: _require_true(check_storage_connection()))


def _require_true(result):
    if not result:
        raise RuntimeError("Dependency check returned false")
