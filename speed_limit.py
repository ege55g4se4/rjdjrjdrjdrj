import asyncio
import time

from main import LINKS

_buckets: dict = {}
_lock = asyncio.Lock()

MIN_RATE = 1024          # 1 KB/s
MIN_BURST = 16 * 1024    # 16 KB

class _Bucket:
    __slots__ = ("rate", "capacity", "tokens", "last")
    def __init__(self, rate: int):
        self.rate = max(rate, MIN_RATE)
        self.capacity = max(self.rate, MIN_BURST)
        self.tokens = self.capacity
        self.last = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last
        if elapsed > 0:
            self.last = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

    async def consume(self, n: int):
        while True:
            self._refill()
            if self.tokens >= n:
                self.tokens -= n
                return
            deficit = n - self.tokens
            wait = deficit / self.rate
            await asyncio.sleep(min(max(wait, 0.005), 0.5))

async def throttle(uuid: str, nbytes: int):
    if nbytes <= 0:
        return
    link = LINKS.get(uuid)
    rate = int((link or {}).get("speed_limit_bytes", 0) or 0)
    if rate <= 0:
        return

    async with _lock:
        bucket = _buckets.get(uuid)
        if bucket is None or bucket.rate != max(rate, MIN_RATE):
            bucket = _Bucket(rate)
            _buckets[uuid] = bucket
    await bucket.consume(nbytes)

def reset_bucket(uuid: str):
    _buckets.pop(uuid, None)