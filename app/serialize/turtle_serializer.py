from typing import List

from io import IOBase

from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.kg.types import LiteralSet, RelationSet
from app.serialize.graph_serializer import GraphSerializer


class TurtleSerialializer(GraphSerializer):
    def write(self, out: IOBase, graph: Graph) -> None:
        ids: List[IRI] = list(graph.get_ids())
        for node_id in sorted(ids):
            meta_properties = dict(
                sorted(graph.get_node_meta_properties(node_id).items())
            )
            for predicate, value in meta_properties.items():
                self.add_property(out, node_id, predicate, value)

            node_properties = dict(sorted(graph.get_node_properties(node_id).items()))
            for predicate, values in node_properties.items():
                if type(values) is set:
                    self.add_properties(out, node_id, predicate, values)
                else:
                    self.add_property(out, node_id, predicate, values)

            node_relations = dict(sorted(graph.get_node_relations(node_id).items()))
            for predicate, values in node_relations.items():
                if type(values) is set:
                    if len(values) == 1:
                        self.add_relation(out, node_id, predicate, next(iter(values)))
                    else:
                        self.add_relations(out, node_id, predicate, values)
                else:
                    self.add_relation(out, node_id, predicate, values)

        out.flush()

    def add_prefix(self, out: IOBase, name: str, uri: str) -> None:
        out.write(f"PREFIX {name} {uri}\n")

    def add_property(
        self, out: IOBase, subject: IRI, predicate: IRI, object: IdBase
    ) -> None:
        rendered_object = (
            f'"{object.render()}"' if object.is_string_type() else object.render()
        )
        out.write(f"{subject.render()} {predicate.render()} {rendered_object} .\n")

    def add_properties(
        self, out: IOBase, subject: IRI, predicate: IRI, values: LiteralSet
    ) -> None:
        collection_subject = " ".join(
            sorted(
                [
                    f'"{v.render()}"' if v.is_string_type() else v.render()
                    for v in values
                ]
            )
        )
        out.write(f"{subject.render()} {predicate.render()} ({collection_subject}) .\n")

    def add_relation(
        self, out: IOBase, subject: IRI, predicate: IRI, object: IRI
    ) -> None:
        out.write(f"{subject.render()} {predicate.render()} {object.render()} .\n")

    def add_relations(
        self, out: IOBase, subject: IRI, predicate: IRI, values: RelationSet
    ) -> None:
        collection_subject = " ".join(sorted([v.render() for v in values]))
        out.write(f"{subject.render()} {predicate.render()} ({collection_subject}) .\n")
