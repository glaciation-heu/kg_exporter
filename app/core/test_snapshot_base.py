from typing import Any, Dict, List, Tuple

import dataclasses
import os.path
from io import FileIO

import yaml

from app.clients.k8s.k8s_client import ResourceSnapshot
from app.core.metric_repository import MetricQuery
from app.core.metric_value import MetricValue
from app.core.types import MetricSnapshot, SliceInputs


class SnapshotTestBase:
    SNAPSHOT_ROOT: str = "app/core/__fixture__/snapshot"

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
            value = self.dataclass_from_dict(MetricValue, query_and_value["value"])
            result.append((query, value))
        return result

    def safe_load_yaml(self, file_path: str) -> Any:
        with FileIO(file_path) as f:
            return yaml.safe_load(f)

    def dataclass_from_dict(self, klass, d):
        try:
            fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
            return klass(
                **{f: self.dataclass_from_dict(fieldtypes[f], d[f]) for f in d}
            )
        except Exception:
            return d  # Not a dataclass field
