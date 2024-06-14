from typing import List, Optional, Tuple

import argparse
from argparse import Namespace
from io import StringIO

from app.clients.influxdb.influxdb_client_impl import InfluxDBClientImpl
from app.clients.k8s.k8s_client_impl import K8SClientImpl
from app.clients.metadata_service.metadata_service_client_impl import (
    MetadataServiceClientImpl,
)
from app.kgexporter_context import KGExporterContext
from app.kgexporter_settings import KGExporterSettings
from app.pydantic_yaml import from_yaml
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.util.clock_impl import ClockImpl


class KGExporterContextBuilder:
    settings: KGExporterSettings

    def __init__(self, settings: KGExporterSettings):
        self.settings = settings

    @staticmethod
    def from_args(args: List[str]) -> Optional["KGExporterContextBuilder"]:
        is_success, config_or_msg = KGExporterContextBuilder.parse_args(args)
        if is_success:
            settings: KGExporterSettings = from_yaml(config_or_msg, KGExporterSettings)  # type: ignore
            return KGExporterContextBuilder(settings)
        else:
            print(config_or_msg)
            return None

    @staticmethod
    def parse_args(args: List[str]) -> Tuple[bool, str]:
        parser = argparse.ArgumentParser(
            description="Kubernetes knowledge graph exporter.", exit_on_error=False
        )
        parser.add_argument(
            "--config",
            dest="config",
            action="store",
            help="Configuration of the KGExporter",
            required=True,
        )

        try:
            ns: Namespace = parser.parse_args(args)
            return True, ns.config
        except argparse.ArgumentError as e:
            message = StringIO()
            parser.print_help(message)
            message.write(str(e))
            return False, message.getvalue()

    def build(self) -> KGExporterContext:
        clock = ClockImpl()
        metadata_client = MetadataServiceClientImpl(self.settings.metadata)
        k8s_client = K8SClientImpl(self.settings.k8s)
        influxdb_client = InfluxDBClientImpl(self.settings.influxdb)
        jsonld_config = JsonLDConfiguration(contexts=dict(), aggregates=set())

        context = KGExporterContext(
            clock,
            metadata_client,
            k8s_client,
            influxdb_client,
            jsonld_config,
            self.settings,
        )
        return context
