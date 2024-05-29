from unittest import TestCase

from app.kg.literal import Literal


class LiteralTest(TestCase):
    def test_eq(self):
        lit1 = Literal("value", Literal.TYPE_STRING)
        lit2 = Literal("value", Literal.TYPE_STRING)
        lit3 = Literal("value1", Literal.TYPE_STRING)

        self.assertEqual(lit1, lit1)
        self.assertEqual(lit1, lit2)
        self.assertNotEqual(lit1, lit3)

    def test_hash(self):
        lit1 = Literal("value", Literal.TYPE_STRING)
        lit2 = Literal("value", Literal.TYPE_STRING)
        lit3 = Literal("value1", Literal.TYPE_STRING)

        self.assertEqual(lit1.__hash__(), lit1.__hash__())
        self.assertEqual(lit1.__hash__(), lit2.__hash__())
        self.assertNotEqual(lit1.__hash__(), lit3.__hash__())

    def test_validation(self):
        with self.assertRaises(Exception) as e:
            Literal("2024-02-13T13:53:43Z", Literal.TYPE_DATE, "%Y-%m-%dT%H:%M:%S%Z")
        self.assertEqual(
            str(e.exception),
            """Unable parse datetime '2024-02-13T13:53:43Z' according to format '%Y-%m-%dT%H:%M:%S%Z'. Error: time data '2024-02-13T13:53:43Z' does not match format '%Y-%m-%dT%H:%M:%S%Z'""",  # noqa: E501
        )

        with self.assertRaises(Exception) as e:
            Literal("2024-02-13T13:53:43Z", Literal.TYPE_DATE)
        self.assertEqual(str(e.exception), "Format is expected for the type 'date'.")

    def test_render(self):
        lit_str = Literal("value", Literal.TYPE_STRING)
        lit_int = Literal(42, Literal.TYPE_INT)
        lit_float = Literal(42.42, Literal.TYPE_FLOAT)
        lit_bool = Literal(True, Literal.TYPE_BOOL)

        self.assertEqual(lit_str.render(), "value")
        self.assertEqual(lit_int.render(), "42")
        self.assertEqual(lit_float.render(), "42.42")
        self.assertEqual(lit_bool.render(), "True")

    def test_string_ops(self):
        lit_str1 = Literal("value1", Literal.TYPE_STRING)
        lit_str2 = Literal("value2", Literal.TYPE_STRING)

        self.assertTrue(lit_str2 > lit_str1)
        self.assertFalse(lit_str2 < lit_str1)
        self.assertTrue(lit_str2 >= lit_str1)
        self.assertTrue(lit_str1 >= lit_str1)
        self.assertFalse(lit_str1 >= lit_str2)
        self.assertTrue(lit_str1 <= lit_str2)
        self.assertTrue(lit_str1 <= lit_str1)
        self.assertFalse(lit_str2 <= lit_str1)

    def test_int_ops(self):
        lit1 = Literal(1, Literal.TYPE_INT)
        lit2 = Literal(2, Literal.TYPE_INT)

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)

    def test_float_ops(self):
        lit1 = Literal(1.1, Literal.TYPE_FLOAT)
        lit2 = Literal(2.2, Literal.TYPE_FLOAT)

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)

    def test_bool_ops(self):
        lit1 = Literal(False, Literal.TYPE_BOOL)
        lit2 = Literal(True, Literal.TYPE_BOOL)

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)

    def test_date_ops(self):
        lit1 = Literal("2024-02-13T13:53:43Z", Literal.TYPE_DATE, "%Y-%m-%dT%H:%M:%S%z")
        lit2 = Literal("2024-02-13T13:53:44Z", Literal.TYPE_DATE, "%Y-%m-%dT%H:%M:%S%z")

        self.assertTrue(lit2 > lit1)
        self.assertFalse(lit2 < lit1)
        self.assertTrue(lit2 >= lit1)
        self.assertTrue(lit1 >= lit1)
        self.assertFalse(lit1 >= lit2)
        self.assertTrue(lit1 <= lit2)
        self.assertTrue(lit1 <= lit1)
        self.assertFalse(lit2 <= lit1)
