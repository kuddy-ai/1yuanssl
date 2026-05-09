"""简单内存限流器。"""

from time import monotonic


class FixedWindowRateLimiter:
    """按 key 进行固定窗口计数的轻量限流器。"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, tuple[float, int]] = {}

    def allow(self, key: str) -> bool:
        now = monotonic()
        window_start, count = self._buckets.get(key, (now, 0))

        if now - window_start >= self.window_seconds:
            self._buckets[key] = (now, 1)
            return True

        if count >= self.max_requests:
            return False

        self._buckets[key] = (window_start, count + 1)
        return True

    def clear(self) -> None:
        self._buckets.clear()
