from tasks.maintenance import health_check_task


def test_health_check_task():
    result = health_check_task.apply(args=[]).get()

    assert result == {
        "status": "ok",
        "service": "fotabo-hashi",
    }
