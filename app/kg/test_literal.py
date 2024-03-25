from unittest import TestCase

from app.kg.literal import Literal


class LiteralTest(TestCase):
    def test_eq(self):
        lit1 = Literal("pref", "value")
        lit2 = Literal("pref", "value")
        lit3 = Literal("pref", "value1")

        self.assertEqual(lit1, lit1)
        self.assertEqual(lit1, lit2)
        self.assertNotEqual(lit1, lit3)

    def test_hash(self):
        lit1 = Literal("pref", "value")
        lit2 = Literal("pref", "value")
        lit3 = Literal("pref", "value1")

        self.assertEqual(lit1.__hash__(), lit1.__hash__())
        self.assertEqual(lit1.__hash__(), lit2.__hash__())
        self.assertNotEqual(lit1.__hash__(), lit3.__hash__())

    def test_render(self):
        lit_str = Literal("value", "str")
        lit_int = Literal(42, "int")
        lit_float = Literal(42.42, "float")
        lit_bool = Literal(True, "bool")

        self.assertEqual(lit_str.render(), "value")
        self.assertEqual(lit_int.render(), "42")
        self.assertEqual(lit_float.render(), "42.42")
        self.assertEqual(lit_bool.render(), "True")

    def test_string_ops(self):
        lit_str1 = Literal("value1", "str")
        lit_str2 = Literal("value2", "str")

        self.assertTrue(lit_str2 > lit_str1)
        self.assertFalse(lit_str2 < lit_str1)
        self.assertTrue(lit_str2 >= lit_str1)
        self.assertTrue(lit_str1 >= lit_str1)
        self.assertFalse(lit_str1 >= lit_str2)
        self.assertTrue(lit_str1 <= lit_str2)
        self.assertTrue(lit_str1 <= lit_str1)
        self.assertFalse(lit_str2 <= lit_str1)

    def test_int_ops(self):
        lit1 = Literal(1, "int")
        lit2 = Literal(2, "int")

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)

    def test_float_ops(self):
        lit1 = Literal(1.1, "float")
        lit2 = Literal(2.2, "float")

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)

    def test_bool_ops(self):
        lit1 = Literal(False, "bool")
        lit2 = Literal(True, "bool")

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)
