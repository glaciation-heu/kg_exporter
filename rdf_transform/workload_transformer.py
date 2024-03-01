
import json
from typing import Any, Dict, List, Tuple
from jsonpath_ng.ext import parse
from rdf_transform.transformer_base import TransformerBase
from rdf_transform.tuple_writer import TupleWriter

class WorkloadToRDFTransformer(TransformerBase):
    sink: TupleWriter

    def __init__(self, source: Dict[str, Any], sink: TupleWriter):
        super().__init__(source)
        self.sink = sink

    def transform(self) -> None:
        name = self.get_id()
        self.sink.write(name, "rdf:type", ":Workload")
        self.write_tuple(name, "rdf:subClassOf", f'$.kind')

        self.write_collection(name, ":has-label", '$.metadata.labels')
        self.write_collection(name, ":has-annotation", '$.metadata.annotations')
        self.write_references(name)

        self.sink.flush()
