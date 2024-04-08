"""Client for Metadata Service"""

import httpx
from httpx import HTTPError

from app.settings import Settings


class ClientError(Exception):
    pass


def send_to_metadata_service(message: str, settings: Settings) -> None:
    """Send graph data to Metadata Service"""
    try:
        httpx.patch(
            settings.metadata_service_url,
            content=message,
            headers=[("Content-Type", "application/json")],
        ).raise_for_status()
    except HTTPError as e:
        raise ClientError(e.args[0]) from e
