from typing import Any, Dict, List, Optional

import yaml
from jsonpath_ng.ext import parse

from app.kg.graph import Graph
from app.kg.iri import IRI
from app.transform.transformation_context import TransformationContext
from app.transform.transformer_base import TransformerBase
from app.transform.upper_ontology_base import UpperOntologyBase


class ClusterToRDFTransformer(TransformerBase, UpperOntologyBase):
    nodes: List[Dict[str, Any]]

    def __init__(
        self, config_map: Dict[str, Any], nodes: List[Dict[str, Any]], sink: Graph
    ):
        TransformerBase.__init__(self, config_map, sink)
        UpperOntologyBase.__init__(self, sink)
        self.nodes = nodes

    def transform(self, _: TransformationContext) -> None:
        config_str = self.get_cluster_configuration()
        if config_str:
            config = yaml.safe_load(config_str)
            cluster_id = self.get_cluster_id(config)
        else:
            cluster_id = IRI(self.CLUSTER_PREFIX, "Unknown")
        self.add_work_producing_resource(cluster_id, "KubernetesCluster")
        for node in self.nodes:
            self.write_node_reference(cluster_id, node)

    def get_cluster_configuration(self) -> Optional[str]:
        config_match = parse("$.data.ClusterConfiguration").find(self.source)
        if len(config_match) == 0:
            return None
        return str(config_match[0].value)

    def get_cluster_id(self, config: Dict[str, Any]) -> IRI:
        cluster_name = parse("$.clusterName").find(config)[0].value
        return IRI(self.CLUSTER_PREFIX, self.escape(cluster_name))

    def write_node_reference(self, cluster_id: IRI, node: Dict[str, Any]) -> None:
        node_id = self.get_node_id(node)
        self.add_work_producing_resource(node_id, "KubernetesWorkerNode")
        self.sink.add_relation(cluster_id, self.HAS_SUBRESOURCE, node_id)
