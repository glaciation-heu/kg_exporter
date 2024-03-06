from app.rdf_transform.tuple_writer import TupleWriter
from io import IOBase

class TurtleWriter(TupleWriter):
    out: IOBase

    def __init__(self, out: IOBase):
        self.out = out
    
    def add_prefix(self, name: str, uri: str) -> None:
        self.out.write(f"PREFIX {name} {uri}\n")
    
    def add_tuple(self, subject: str, predicate: str, object: str) -> None:
        self.out.write(f"{subject} {predicate} {object} .\n")

    def flush(self) -> None:
        self.out.flush()