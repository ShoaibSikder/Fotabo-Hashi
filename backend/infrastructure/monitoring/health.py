from .checks import check_database_connection, check_redis_connection, check_storage


def get_readiness_status():
    checks = {
        "database": check_database_connection(),
        "redis": check_redis_connection(),
        "storage": check_storage(),
    }
    ready = all(item["status"] == "ok" for item in checks.values())
    return {"status": "ok" if ready else "error", "checks": checks}
