from typing import Any, Dict

from app.rdf_transform.transformer_base import TransformerBase
from app.rdf_transform.tuple_writer import TupleWriter


class WorkloadToRDFTransformer(TransformerBase):
    def __init__(self, source: Dict[str, Any], sink: TupleWriter):
        super().__init__(source, sink)

    def transform(self) -> None:
        name = self.get_id()
        self.sink.add_tuple(name, "rdf:type", ":Workload")
        self.write_tuple(name, "rdf:subClassOf", "$.kind")

        self.write_collection(name, ":has-label", "$.metadata.labels")
        self.write_collection(name, ":has-annotation", "$.metadata.annotations")
        self.write_references(name)

        self.sink.flush()
