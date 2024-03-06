
from io import StringIO
from app.rdf_transform.test_base import TransformBaseTest
from app.rdf_transform.node_transformer import NodesToRDFTransformer
from app.rdf_transform.turtle_writer import TurtleWriter

class NodeTransformerTest(TransformBaseTest):
    def setUp(self):        
        self.maxDiff = None

    def test_transform(self):
        self.transform("master_node")
        self.transform("worker_node")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        NodesToRDFTransformer(node_json, TurtleWriter(buffer)).transform()
        self.assertEqual(buffer.getvalue(), node_turtle)
