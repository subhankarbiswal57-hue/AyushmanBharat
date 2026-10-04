"""
tests/test_rate_limiter.py
──────────────────────────
Unit tests for shared.rate_limiter — no external services required.
Run with:  pytest tests/test_rate_limiter.py -v
"""
import time
import threading
import pytest

from shared.rate_limiter import RateLimiter


class TestRateLimiterBasics:
    """Core allow / deny behaviour."""

    def test_allows_requests_within_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.is_allowed("user-A") is True

    def test_blocks_request_exceeding_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.is_allowed("user-B")
        assert limiter.is_allowed("user-B") is False

    def test_different_keys_are_independent(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.is_allowed("ip-1")
        limiter.is_allowed("ip-1")
        # ip-1 is now blocked, ip-2 should still be free
        assert limiter.is_allowed("ip-1") is False
        assert limiter.is_allowed("ip-2") is True

    def test_remaining_decrements_correctly(self):
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        limiter.is_allowed("user-C")
        limiter.is_allowed("user-C")
        assert limiter.remaining("user-C") == 8

    def test_remaining_is_zero_when_blocked(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.is_allowed("user-D")
        limiter.is_allowed("user-D")
        assert limiter.remaining("user-D") == 0


class TestRateLimiterWindow:
    """Sliding-window expiry behaviour."""

    def test_window_resets_after_expiry(self):
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        limiter.is_allowed("user-E")
        limiter.is_allowed("user-E")
        assert limiter.is_allowed("user-E") is False
        time.sleep(1.05)                          # wait for window to expire
        assert limiter.is_allowed("user-E") is True

    def test_sliding_window_does_not_reset_all_at_once(self):
        """Only the timestamps older than window_seconds should be evicted."""
        limiter = RateLimiter(max_requests=3, window_seconds=2)
        limiter.is_allowed("user-F")              # t=0
        time.sleep(1.1)
        limiter.is_allowed("user-F")              # t=1.1
        limiter.is_allowed("user-F")              # t=1.1 (nearly)
        # All 3 slots used; still blocked
        assert limiter.is_allowed("user-F") is False
        time.sleep(1.1)
        # First request (t=0) has now expired; one slot opens
        assert limiter.is_allowed("user-F") is True


class TestRateLimiterConcurrency:
    """Thread-safety under concurrent load."""

    def test_concurrent_requests_do_not_exceed_limit(self):
        max_req = 50
        limiter = RateLimiter(max_requests=max_req, window_seconds=60)
        allowed_count = 0
        lock = threading.Lock()

        def make_request():
            nonlocal allowed_count
            if limiter.is_allowed("shared-key"):
                with lock:
                    allowed_count += 1

        threads = [threading.Thread(target=make_request) for _ in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert allowed_count == max_req, (
            f"Expected exactly {max_req} allowed, got {allowed_count}"
        )


class TestPreConfiguredLimiters:
    """Sanity-check the pre-wired limiter instances."""

    def test_auth_limiter_blocks_after_5(self):
        from shared.rate_limiter import auth_limiter
        key = "test-auth-ip"
        for _ in range(5):
            auth_limiter.is_allowed(key)
        assert auth_limiter.is_allowed(key) is False

    def test_api_limiter_has_higher_threshold(self):
        from shared.rate_limiter import api_limiter, auth_limiter
        assert api_limiter.max_requests > auth_limiter.max_requests
