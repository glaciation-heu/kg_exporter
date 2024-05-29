class TransformationContext:
    timestamp: int

    def __init__(self, timestamp: int):
        self.timestamp = timestamp

    def get_timestamp(self) -> int:
        return self.timestamp
