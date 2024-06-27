from typing import Any, Dict, List, Optional, Tuple

import argparse
from argparse import Namespace
from io import StringIO

from app.clients.k8s.k8s_client_impl import K8SClientImpl
from app.clients.metadata_service.metadata_service_client_impl import (
    MetadataServiceClientImpl,
)
from app.clients.prometheus.prometheus_client import PrometheusClient
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.id_base import IdBase
from app.kg.iri import IRI
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
        prometheus_client = PrometheusClient(self.settings.prometheus_client)
        jsonld_config = self.get_jsonld_config()

        context = KGExporterContext(
            clock,
            metadata_client,
            k8s_client,
            prometheus_client,
            jsonld_config,
            self.settings,
        )
        return context

    def get_jsonld_config(self) -> JsonLDConfiguration:
        contexts: Dict[IdBase, Dict[str, Any]] = {
            JsonLDConfiguration.DEFAULT_CONTEXT_IRI: {
                "k8s": "http://glaciation-project.eu/model/k8s/",
                "glc": "https://glaciation-heu.github.io/models/reference_model.turtle",
                "cluster": "https://127.0.0.1:6443/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            }
        }
        return JsonLDConfiguration(
            contexts,
            {
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "WorkProducingResource"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "Aspect"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "MeasurementProperty"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "MeasuringResource"),
                IRI(UpperOntologyBase.GLACIATION_PREFIX, "MeasurementUnit"),
            },
        )
