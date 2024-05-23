import json
from io import StringIO

from app.k8s_transform.replicaset_transformer import ReplicaSetToRDFTransformer
from app.k8s_transform.test_base import TransformBaseTest
from app.k8s_transform.transformation_context import TransformationContext
from app.kg.inmemory_graph import InMemoryGraph
from app.serialize.jsonld_serializer import JsonLDSerialializer
from app.serialize.turtle_serializer import TurtleSerialializer


class ReplicaSetTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform_turtle(self):
        self.transform_turtle("replicaset")

    def transform_turtle(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        ReplicaSetToRDFTransformer(node_json, graph).transform(context)
        TurtleSerialializer().write(buffer, graph)
        # print(buffer.getvalue())
        self.assertEqual(buffer.getvalue(), node_turtle)

    def test_transform_jsonld(self):
        self.transform_jsonld("replicaset")

    def transform_jsonld(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_jsonld = self.load_jsonld(file_id)

        buffer = StringIO()
        graph = InMemoryGraph()
        context = TransformationContext(123)
        ReplicaSetToRDFTransformer(node_json, graph).transform(context)
        JsonLDSerialializer(self.get_jsonld_config()).write(buffer, graph)
        # print(buffer.getvalue())
        self.assertEqual(json.loads(buffer.getvalue()), node_jsonld)
