
from io import StringIO
from unittest import TestCase

from rdf_transform.node_transformer import NodesToRDFTransformer
from rdf_transform.turtle_writer import TurtleWriter

class TurtleWriterTest(TestCase):
    def setUp(self):        
        pass

    def test_empty(self):
        buffer = StringIO()
        writer = TurtleWriter(buffer)
        writer.flush()        
        self.assertEqual(buffer.getvalue(), "")

    def test_tuples(self):
        buffer = StringIO()
        writer = TurtleWriter(buffer)
        writer.add_tuple("one", "two", "three")
        writer.add_tuple("four", "five", "six")
        writer.flush()        
        self.assertEqual(buffer.getvalue(), "one two three .\nfour five six .\n")