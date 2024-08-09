from typing import Any, Dict, List, Set

import json
from urllib.parse import urlsplit, urlunsplit

from app.kg.id_base import IdBase
from app.kg.iri import IRI
from app.kg.literal import Literal


class QueryResponseParser:
    def parse(self, response_str: str) -> List[Dict[str, IdBase]]:
        response = json.loads(response_str)
        variable_names = self.get_variables(response)
        if len(variable_names) == 0:
            return []
        return self.parse_rows(variable_names, response)

    def get_variables(self, response: Dict[str, Any]) -> Set[str]:
        head = response.get("head") or dict()
        return set(head.get("vars") or {})

    def parse_rows(
        self, variable_names: Set[str], response: Dict[str, Any]
    ) -> List[Dict[str, IdBase]]:
        results = response.get("results") or dict()
        bindings = results.get("bindings") or []
        return [self.parse_row(variable_names, binding) for binding in bindings]

    def parse_row(
        self, variable_names: Set[str], binding: Dict[str, Any]
    ) -> Dict[str, IdBase]:
        row = dict()
        for name in variable_names:
            field = binding.get(name)
            if field:
                row[name] = self.parse_value(field)
        return row

    def parse_value(self, field: Dict[str, Any]) -> IdBase:
        value_type = field.get("type")
        if value_type == "uri":
            result = self.parse_uri(field)
            return result
        elif value_type == "literal":
            return self.parse_literal(field)
        else:
            raise Exception(f"Unexpected value_type {value_type}")

    def parse_literal(self, field: Dict[str, Any]) -> Literal:
        value = field.get("value")
        return Literal(str(value), Literal.TYPE_STRING)

    def parse_uri(self, field: Dict[str, Any]) -> IRI:
        value = field.get("value")

        addressing, location, path, query, fragment_identifier = urlsplit(value)
        if len(fragment_identifier) != 0:
            prefix = urlunsplit((addressing, location, path, query, ""))  # type: ignore
            return IRI(str(prefix), str(fragment_identifier))

        path_tokens = str(path.split("/"))  # type: ignore
        if len(path_tokens) > 0:
            new_path, identifier = path_tokens[:-1], path_tokens[-1]
            prefix = urlunsplit((addressing, location, "/".join(new_path), query, ""))  # type: ignore
            if prefix[-1] == ":":  # type: ignore
                prefix = prefix[:-1]  # type: ignore
            return IRI(prefix, identifier)  # type: ignore

        raise Exception(f"unrecognized IRI {value}")
