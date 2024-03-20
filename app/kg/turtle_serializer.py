from io import IOBase

from app.kg.graph import Graph
from app.kg.graph_serializer import GraphSerializer


class TurtleSerialializer(GraphSerializer):
    def write(self, out: IOBase, graph: Graph) -> None:
        for node_id in sorted(graph.get_ids()):
            meta_properties = dict(
                sorted(graph.get_node_meta_properties(node_id).items())
            )
            for predicate, value in meta_properties.items():
                self.add_tuple(out, node_id, f"{predicate}", value)

            node_properties = dict(sorted(graph.get_node_properties(node_id).items()))
            for predicate, values in node_properties.items():
                if type(values) is set:
                    collection_subject = " ".join(sorted(values))
                    self.add_tuple(
                        out, node_id, f"{predicate}", f"({collection_subject})"
                    )
                else:
                    self.add_tuple(out, node_id, f"{predicate}", values)

            node_relations = dict(sorted(graph.get_node_relations(node_id).items()))
            for predicate, values in node_relations.items():
                if type(values) is set:
                    if len(values) == 1:
                        self.add_tuple(out, node_id, f"{predicate}", next(iter(values)))
                    else:
                        collection_subject = " ".join(sorted(values))
                        self.add_tuple(
                            out, node_id, f"{predicate}", f"({collection_subject})"
                        )
                else:
                    self.add_tuple(out, node_id, f"{predicate}", values)

        out.flush()

    def add_prefix(self, out: IOBase, name: str, uri: str) -> None:
        out.write(f"PREFIX {name} {uri}\n")

    def add_tuple(self, out: IOBase, subject: str, predicate: str, object: str) -> None:
        out.write(f"{subject} {predicate} {object} .\n")
