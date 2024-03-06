from io import StringIO

from app.rdf_transform.replicaset_transformer import ReplicaSetToRDFTransformer
from app.rdf_transform.test_base import TransformBaseTest
from app.rdf_transform.turtle_writer import TurtleWriter


class ReplicaSetTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform(self):
        self.transform("replicaset")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        ReplicaSetToRDFTransformer(node_json, TurtleWriter(buffer)).transform()
        self.assertEqual(buffer.getvalue(), node_turtle)
