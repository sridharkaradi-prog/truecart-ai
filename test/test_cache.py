import time

import pytest

from truecart_ai.services.cache import TTLCache


def test_cache_returns_stored_value() -> None:

    cache = TTLCache(
        ttl_seconds=60
    )

    cache.set(
        "tata:411028",
        {"price": "30.00"},
    )

    value, hit = cache.get(
        "tata:411028"
    )

    assert hit is True
    assert value == {
        "price": "30.00"
    }


def test_cache_expires_values() -> None:

    cache = TTLCache(
        ttl_seconds=0.01
    )

    cache.set(
        "tata:411028",
        {"price": "30.00"},
    )

    time.sleep(0.02)

    value, hit = cache.get(
        "tata:411028"
    )

    assert hit is False
    assert value is None


def test_cache_clear_removes_all_entries() -> None:

    cache = TTLCache(
        ttl_seconds=60
    )

    cache.set(
        "one",
        1,
    )

    cache.set(
        "two",
        2,
    )

    assert cache.size() == 2

    cache.clear()

    assert cache.size() == 0

    value, hit = cache.get(
        "one"
    )

    assert hit is False
    assert value is None