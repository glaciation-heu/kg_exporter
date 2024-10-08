import asyncio

from vcr.unittest import VCRTestCase

from app.clients.metadata_service.metadata_service_client_impl import (
    ClientError,
    MetadataServiceClientImpl,
)
from app.clients.metadata_service.metadata_service_settings import (
    MetadataServiceSettings,
)
from app.kg.iri import IRI
from app.kg.literal import Literal


class MetadataServiceClientTest(VCRTestCase):
    def test_insert_success(self):
        settings = MetadataServiceSettings()
        client = MetadataServiceClientImpl(settings)
        asyncio.run(client.insert("metadata-service", "{}"))

    def test_insert_failure(self):
        settings = MetadataServiceSettings()
        client = MetadataServiceClientImpl(settings)
        with self.assertRaises(ClientError) as e:
            asyncio.run(client.insert("metadata-service", "{}"))
        msg = (
            "Client error '404 Not Found' for url 'http://metadata-service/api/v0/graph'\n"
            "For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404"
        )
        self.assertEqual(msg, str(e.exception))

    def test_query_success(self):
        settings = MetadataServiceSettings()
        client = MetadataServiceClientImpl(settings)
        results = asyncio.run(client.query("metadata-service", "query"))
        self.assertEqual(
            results,
            [
                {
                    "obj": Literal("Halloumi", Literal.TYPE_STRING),
                    "pred": IRI("glc", "property"),
                    "sub": IRI(
                        "https://kubernetes.local/",
                        "kafka.kafka-broker-1.kafka-init.Status",
                    ),
                },
            ],
        )
