from unittest import TestCase

from app.kg.iri import IRI


class IRITest(TestCase):
    def test_eq(self):
        iri1 = IRI("pref", "value")
        iri2 = IRI("pref", "value")
        iri3 = IRI("pref", "value1")

        self.assertEqual(iri1, iri1)
        self.assertEqual(iri1, iri2)
        self.assertNotEqual(iri1, iri3)

    def test_hash(self):
        iri1 = IRI("pref", "value")
        iri2 = IRI("pref", "value")
        iri3 = IRI("pref", "value1")

        self.assertEqual(iri1.__hash__(), iri1.__hash__())
        self.assertEqual(iri1.__hash__(), iri2.__hash__())
        self.assertNotEqual(iri1.__hash__(), iri3.__hash__())

    def test_render(self):
        iri = IRI("pref", "value")

        self.assertEqual(iri.render(), "pref:value")
