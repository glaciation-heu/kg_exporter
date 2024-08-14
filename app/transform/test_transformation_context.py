import unittest

from app.transform.transformation_context import TransformationContext
from app.transform.upper_ontology_base import UpperOntologyBase


class TransformationContextTest(unittest.TestCase):
    def test_get_timestamp_as_str(self) -> None:
        self.assertEqual(
            "2024-08-13T12:54:13Z",
            TransformationContext(1723553653000).get_timestamp_as_str(
                UpperOntologyBase.DATETIME_FORMAT
            ),
        )
