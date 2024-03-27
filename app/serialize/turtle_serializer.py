from typing import Dict, List

from io import IOBase

from app.kg.graph import Graph
from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.kg.literal import Literal
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
                if isinstance(values, set):
                    self.add_properties(out, node_id, predicate, values)
                else:
                    self.add_property(out, node_id, predicate, values)

            node_relations: Dict[IRI, RelationSet] = dict(
                sorted(graph.get_node_relations(node_id).items())
            )
            for predicate, relation_objects in node_relations.items():
                if len(relation_objects) == 1:
                    relation_iri: IRI = next(iter(relation_objects))
                    self.add_relation(out, node_id, predicate, relation_iri)
                else:
                    self.add_relations(out, node_id, predicate, relation_objects)

        out.flush()

    def add_prefix(self, out: IOBase, name: str, uri: str) -> None:
        out.write(f"PREFIX {name} {uri}\n")

    def add_property(
        self, out: IOBase, subject: IRI, predicate: IRI, object: IdBase
    ) -> None:
        out.write(
            f"{subject.render()} {predicate.render()} {self.get_value(object)} .\n"
        )

    def add_properties(
        self, out: IOBase, subject: IRI, predicate: IRI, values: LiteralSet
    ) -> None:
        collection_subject = " ".join(sorted([self.get_value(v) for v in values]))
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

    def get_value(self, base: IdBase) -> str:
        if isinstance(base, Literal):
            if base._type == Literal.TYPE_STRING:
                return f'"{base.value}"'
            elif base._type == Literal.TYPE_INT or base._type == Literal.TYPE_FLOAT:
                return f"{base.value}^^<http://www.w3.org/2001/XMLSchema#integer>"
            elif base._type == Literal.TYPE_BOOL:
                return f"{base.value}^^<http://www.w3.org/2001/XMLSchema#boolean>"
            else:
                raise Exception(
                    f"""Unexpected type {base._type},
                    must one of ('{Literal.TYPE_STRING}', '{Literal.TYPE_INT}',
                    '{Literal.TYPE_FLOAT}', '{Literal.TYPE_BOOL}')"""
                )
        elif isinstance(base, IRI):
            return base.render()
        else:
            raise Exception(f"Unexpected type {type(base)}, must one of (Literal, IRI)")
