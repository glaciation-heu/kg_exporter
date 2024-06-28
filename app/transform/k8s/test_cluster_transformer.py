import json
from io import StringIO

from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.serialize.turtle_serializer import TurtleSerialializer
from app.transform.k8s.cluster_transformer import ClusterToRDFTransformer
from app.transform.k8s.test_base import TransformBaseTest
from app.transform.k8s.transformation_context import TransformationContext


class ClusterTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self):
        self.transform_turtle("cluster")

    def transform_turtle(self, file_id: str) -> None:
        config_map_json = self.load_json(f"{file_id}.kubeadm-config")
        nodes_json = self.load_json_list(f"{file_id}.nodes")
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        ClusterToRDFTransformer(config_map_json, nodes_json, graph).transform(context)
        TurtleSerialializer().write(buffer, graph)
        self.assertEqual(buffer.getvalue(), node_turtle)

    def test_transform_jsonld(self):
        self.transform_jsonld("cluster")

    def transform_jsonld(self, file_id: str) -> None:
        config_map_json = self.load_json(f"{file_id}.kubeadm-config")
        nodes_json = self.load_json_list(f"{file_id}.nodes")
        node_jsonld = self.load_jsonld(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        ClusterToRDFTransformer(config_map_json, nodes_json, graph).transform(context)
        JsonLDSerialializer(self.get_jsonld_config()).write(buffer, graph)
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)
