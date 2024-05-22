from typing import Any, Dict, List

import yaml
from jsonpath_ng.ext import parse

from app.k8s_transform.transformer_base import TransformerBase
from app.k8s_transform.upper_ontology_base import UpperOntologyBase
from app.kg.graph import Graph
from app.kg.iri import IRI


class ClusterToRDFTransformer(TransformerBase, UpperOntologyBase):
    nodes: List[Dict[str, Any]]

    def __init__(
        self, config_map: Dict[str, Any], nodes: List[Dict[str, Any]], sink: Graph
    ):
        TransformerBase.__init__(self, config_map, sink)
        UpperOntologyBase.__init__(self, sink)
        self.nodes = nodes

    def transform(self) -> None:
        config_str: str = self.get_cluster_configuration()
        config = yaml.safe_load(config_str)
        cluster_id = self.get_cluster_id(config)
        self.add_work_producing_resource(cluster_id, "KubernetesCluster")
        for node in self.get_nodes():
            self.write_node_reference(cluster_id, node)

    def get_cluster_configuration(self) -> str:
        return str(parse("$.data.ClusterConfiguration").find(self.source)[0].value)

    def get_cluster_id(self, config: Dict[str, Any]) -> IRI:
        cluster_name = parse("$.clusterName").find(config)[0].value
        return IRI(self.CLUSTER_PREFIX, self.escape(cluster_name))

    def get_nodes(self) -> List[Dict[str, Any]]:
        return list(parse("$.items").find(self.nodes)[0].value)

    def write_node_reference(self, cluster_id: IRI, node: Dict[str, Any]) -> None:
        node_id = self.get_node_id(node)
        self.sink.add_relation(cluster_id, self.HAS_SUBRESOURCE, node_id)
        self.sink.add_meta_property(
            node_id,
            Graph.RDF_TYPE_IRI,
            IRI(self.GLACIATION_PREFIX, "WorkProducingResource"),
        )
