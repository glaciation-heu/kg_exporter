import pytest

from app.clients.metadata import ClientError, send_to_metadata_service
from app.settings import Settings


def test__call_send_to_invalid_host__raises() -> None:
    settings = Settings(metadata_service_url="http://example.fake/api")
    with pytest.raises(ClientError) as e:
        send_to_metadata_service("{}", settings)
    assert isinstance(e.value, ClientError)


@pytest.mark.vcr()
def test__call_send_to_valid_endpoint__no_exception() -> None:
    settings = Settings()
    send_to_metadata_service("{}", settings)


@pytest.mark.vcr()
def test__call_send_to_404_endpoint__raises() -> None:
    settings = Settings()
    settings.metadata_service_url = settings.metadata_service_url + "fake_url"

    with pytest.raises(ClientError, match="404 Not Found") as e:
        send_to_metadata_service("{}", settings)

    assert isinstance(e.value, ClientError)
