from io import StringIO

from app.rdf_transform.pod_transformer import PodToRDFTransformer
from app.rdf_transform.test_base import TransformBaseTest
from app.rdf_transform.turtle_writer import TurtleWriter


class PodTransformerTest(TransformBaseTest):
    def setUp(self):
        self.maxDiff = None

    def test_transform(self):
        self.transform("pod1")
        self.transform("pod2")
        self.transform("pod3")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        PodToRDFTransformer(node_json, TurtleWriter(buffer)).transform()
        self.assertEqual(buffer.getvalue(), node_turtle)
