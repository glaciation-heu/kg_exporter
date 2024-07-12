from unittest import TestCase

from app.kgexporter_context_builder import KGExporterContextBuilder


class KGExporterContextBuilderTest(TestCase):
    def test_success(self) -> None:
        is_success, path = KGExporterContextBuilder.parse_args(
            ["--config", "./etc/config.yaml"]
        )
        self.assertTrue(is_success)
        self.assertEqual(path, "./etc/config.yaml")

    def test_failure(self) -> None:
        is_success, msg = KGExporterContextBuilder.parse_args(["--config"])
        self.assertFalse(is_success)
        self.assertEqual(
            msg,
            (
                "usage: pytest [-h] --config CONFIG\n\n"
                "Kubernetes knowledge graph exporter.\n\n"
                + "options:\n"
                + "  -h, --help       show this help message and exit\n"
                + "  --config CONFIG  Configuration of the KGExporter\n"
                + "argument --config: expected one argument"
            ),
        )
