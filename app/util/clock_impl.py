import time

from app.util.clock import Clock


class ClockImpl(Clock):
    def now_seconds(self) -> int:
        return int(time.time())
