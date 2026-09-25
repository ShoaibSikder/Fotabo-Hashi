import pytest

from infrastructure.cache.services import check_cache_connection, delete_cached, get_cached, set_cached


@pytest.mark.django_db
def test_cache_set_get():
    set_cached("test:key", {"status": "ok"}, timeout=30)
    assert get_cached("test:key") == {"status": "ok"}


@pytest.mark.django_db
def test_cache_delete():
    set_cached("test:key", "value", timeout=30)
    delete_cached("test:key")
    assert get_cached("test:key") is None


@pytest.mark.django_db
def test_cache_connection():
    assert check_cache_connection() is True
