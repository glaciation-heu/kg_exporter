
import json
from unittest import TestCase
from io import FileIO, StringIO
from rdf_transform.turtle_writer import TurtleWriter
from rdf_transform.workload_transformer import WorkloadToRDFTransformer

class WorkloadTransformerTest(TestCase):
    def setUp(self):        
        self.maxDiff = None

    def test_transform(self):
        self.transform("deployment")
        self.transform("statefulset")

    def transform(self, file_id: str) -> None:
        node_json = self.load_json(file_id)
        node_turtle = self.load_turtle(file_id)

        buffer = StringIO()
        WorkloadToRDFTransformer(node_json, TurtleWriter(buffer)).transform()
        # print(buffer.getvalue())
        self.assertEqual(buffer.getvalue(), node_turtle)

    def load_turtle(self, name: str) -> str:
        with FileIO(f"rdf_transform/__fixture__/{name}.turtle") as f:
            return f.readall().decode("utf-8")
    
    def load_json(self, name: str) -> str:
        with FileIO(f"rdf_transform/__fixture__/{name}.json") as f:
            return json.load(f)

