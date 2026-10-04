"""
Thread-safe in-memory LRU Cache with TTL expiry for Ayushman Bharat microservices.
Ideal for caching triage lookup results, symptom-disease knowledge graphs, and ABHA public keys.
"""

import time
import threading
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict


class TTLCache:
    """
    Least-Recently-Used (LRU) Cache with Time-To-Live (TTL) expiration per key.
    Thread-safe implementation with locking for concurrent async workers.
    """

    def __init__(self, maxsize: int = 1000, default_ttl_seconds: int = 300):
        self.maxsize = maxsize
        self.default_ttl = default_ttl_seconds
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default

            value, expires_at = self._cache[key]
            if time.time() > expires_at:
                del self._cache[key]
                self._misses += 1
                return default

            self._cache.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        with self._lock:
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            expires_at = time.time() + ttl

            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, expires_at)

            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) if total_requests > 0 else 0.0
            return {
                "size": len(self._cache),
                "maxsize": self.maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
            }


# Global shared cache instances
triage_cache = TTLCache(maxsize=2000, default_ttl_seconds=600)
auth_token_cache = TTLCache(maxsize=5000, default_ttl_seconds=900)
