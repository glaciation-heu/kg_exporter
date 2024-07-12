from app.util.clock import Clock


class MockClock(Clock):
    seconds: int

    def __init__(self):
        self.seconds = 1

    def set_seconds(self, seconds: int) -> None:
        self.seconds = seconds

    def now_seconds(self) -> int:
        return self.seconds
