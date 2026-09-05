from dataclasses import dataclass
from time import monotonic
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    """
    Small in-memory cache with time-based expiration.

    Intended for the MVP and local deployment.
    A distributed cache such as Redis can replace this
    implementation later without changing callers.
    """

    def __init__(self, ttl_seconds: float = 60.0) -> None:
        if ttl_seconds <= 0:
            raise ValueError(
                "ttl_seconds must be greater than zero."
            )

        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, CacheEntry] = {}

    def get(self, key: str) -> tuple[Any | None, bool]:

        entry = self._entries.get(key)

        if entry is None:
            return None, False

        if monotonic() >= entry.expires_at:

            del self._entries[key]

            return None, False

        return entry.value, True

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._entries[key] = CacheEntry(
            value=value,
            expires_at=(
                monotonic()
                + self.ttl_seconds
            ),
        )

    def clear(self) -> None:
        self._entries.clear()

    def size(self) -> int:
        return len(self._entries)