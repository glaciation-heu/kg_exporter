from typing import Any, Dict, List, Tuple

import dataclasses
import json
import os.path
from io import FileIO, StringIO

import yaml

from app.clients.influxdb.mock_infuxdbclient import MockInfluxDBClient
from app.clients.k8s.k8s_client import ResourceSnapshot
from app.clients.k8s.mock_k8s_client import MockK8SClient
from app.core.kg_builder import QuerySettings
from app.core.metric_repository import MetricQuery, ResultParserId
from app.core.metric_value import MetricValue
from app.core.types import KGSliceId, MetricSnapshot, SliceInputs
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.serialize.jsonld_configuration import JsonLDConfiguration
from app.serialize.jsonld_serializer import JsonLDSerialializer


class SnapshotTestBase:
    SNAPSHOT_ROOT: str = "app/core/__fixture__/snapshot"

    def mock_inputs(
        self,
        identity: str,
        k8s_client: MockK8SClient,
        influxdb_client: MockInfluxDBClient,
        settings: QuerySettings,
    ) -> None:
        resources = self.load_k8s_snapshot(identity)

        k8s_client.mock_cluster(resources.cluster)
        k8s_client.mock_daemonsets(resources.daemonsets)
        k8s_client.mock_deployments(resources.deployments)
        k8s_client.mock_jobs(resources.jobs)
        k8s_client.mock_nodes(resources.nodes)
        k8s_client.mock_pods(resources.pods)
        k8s_client.mock_replicasets(resources.replicasets)
        k8s_client.mock_statefullsets(resources.statefullsets)

        metrics = self.load_metric_snapshot(identity)
        for query, value in metrics.node_metrics:
            influxdb_client.mock_query(query.query, [value])
            settings.node_queries.append(query)

        for query, value in metrics.pod_metrics:
            influxdb_client.mock_query(query.query, [value])
            settings.pod_queries.append(query)

    def get_inputs(self, identity: str) -> SliceInputs:
        resource_snapshot = self.load_k8s_snapshot(identity)
        metric_snapshot = self.load_metric_snapshot(identity)
        inputs = SliceInputs(resource_snapshot, metric_snapshot)
        return inputs

    def load_k8s_snapshot(self, snapshot_id: str) -> ResourceSnapshot:
        return ResourceSnapshot(
            cluster=self.load_yaml(snapshot_id, "k8s_cluster"),  # type: ignore
            pods=self.load_yaml(snapshot_id, "k8s_pods"),
            nodes=self.load_yaml(snapshot_id, "k8s_nodes"),
            deployments=self.load_yaml(snapshot_id, "k8s_deployments"),
            jobs=self.load_yaml(snapshot_id, "k8s_jobs"),
            statefullsets=self.load_yaml(snapshot_id, "k8s_statefullsets"),
            daemonsets=self.load_yaml(snapshot_id, "k8s_daemonsets"),
            replicasets=self.load_yaml(snapshot_id, "k8s_replicasets"),
        )

    def load_metric_snapshot(self, snapshot_id: str) -> MetricSnapshot:
        return MetricSnapshot(
            pod_metrics=self.load_metrics(snapshot_id, "metric_pods"),
            node_metrics=self.load_metrics(snapshot_id, "metric_nodes"),
        )

    def load_yaml(self, snapshot_id: str, file_id: str) -> List[Dict[str, Any]]:
        file_path = f"{self.SNAPSHOT_ROOT}/{snapshot_id}/{file_id}.yaml"
        if not os.path.exists(file_path):
            return []
        return self.safe_load_yaml(file_path)  # type: ignore

    def load_metrics(
        self, snapshot_id: str, file_id: str
    ) -> List[Tuple[MetricQuery, MetricValue]]:
        file_path = f"{self.SNAPSHOT_ROOT}/{snapshot_id}/{file_id}.yaml"
        if not os.path.exists(file_path):
            return []
        query_and_values: List[Dict[str, Any]] = self.safe_load_yaml(file_path)
        result = []
        for query_and_value in query_and_values:
            query = self.dataclass_from_dict(MetricQuery, query_and_value["query"])
            query.result_parser = ResultParserId.SIMPLE_RESULT_PARSER  # TODO parse
            value = self.dataclass_from_dict(MetricValue, query_and_value["value"])
            result.append((query, value))
        return result

    def safe_load_yaml(self, file_path: str) -> Any:
        with FileIO(file_path) as f:
            return yaml.safe_load(f)

    def load_jsonld(self, file_path: str) -> Dict[str, Any]:
        with FileIO(file_path) as f:
            return json.load(f)  # type: ignore

    def dataclass_from_dict(self, klass, d):
        try:
            fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
            return klass(
                **{f: self.dataclass_from_dict(fieldtypes[f], d[f]) for f in d}
            )
        except Exception:
            return d  # Not a dataclass field

    def assert_graph(self, graph: Graph, snapshot_id: str, slice_id: KGSliceId) -> None:
        file_path = f"{self.SNAPSHOT_ROOT}/{snapshot_id}/slice_{slice_id.node_ip}_{slice_id.port}.jsonld"
        node_jsonld = self.load_jsonld(file_path)

        buffer = StringIO()
        JsonLDSerialializer(self.get_test_jsonld_config()).write(buffer, graph)
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)  # type: ignore

    def assert_serialized_graph(
        self, snapshot_id: str, slice_id: KGSliceId, actual_graph: str
    ) -> None:
        file_path = f"{self.SNAPSHOT_ROOT}/{snapshot_id}/slice_{slice_id.node_ip}_{slice_id.port}.jsonld"
        node_jsonld = self.load_jsonld(file_path)

        self.assertEqual(json.loads(actual_graph), node_jsonld)  # type: ignore

    def get_test_jsonld_config(self) -> JsonLDConfiguration:
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
