import pytest

from app.client import send_to_metadata_service, ClientError
from app.settings import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        metadata_service_url="http://example.fake/api"
    )


def test__call_send_to_invalid_host__raises(
    settings: Settings
) -> None:
    with pytest.raises(ClientError) as e:
        send_to_metadata_service("{}", settings)


# E2E test
def test__call_send_to_valid_endpoint__no_exception() -> None:
    settings = Settings()
    send_to_metadata_service("{}", settings)


# E2E test
def test__call_send_to_404_endpoint__raises() -> None:
    settings = Settings()
    settings.metadata_service_url = settings.metadata_service_url +"test"
    with pytest.raises(ClientError) as e:
        send_to_metadata_service("{}", settings)