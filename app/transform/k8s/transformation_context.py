import datetime


class TransformationContext:
    timestamp: int

    def __init__(self, timestamp: int):
        self.timestamp = timestamp

    def get_timestamp(self) -> int:
        return self.timestamp

    def get_timestamp_as_str(self, format: str) -> str:
        now_datetime = datetime.datetime.fromtimestamp(self.timestamp / 1000)
        return now_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
