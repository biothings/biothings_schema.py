import os.path
import unittest

from biothings_schema import Schema, SchemaClass, SchemaProperty

_CURRENT = os.path.abspath(os.path.dirname(__file__))


class TestSchemaClass(unittest.TestCase):
    """Test Schema Validator Class"""

    def setUp(self):
        schema_file = os.path.join(_CURRENT, "data", "class_override.json")
        self.se = Schema(schema_file)

    def test_list_all_classes(self):
        """Test list_all_classes function"""
        all_cls = self.se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]
        # assert only one class bioschemas:Gene
        self.assertEqual(["bioschemas:Gene"], all_cls_names)

    def test_list_all_properties(self):
        """Test list_all_properties function"""
        all_props = self.se.list_all_properties()
        all_prop_names = [_prop.name for _prop in all_props]
        # assert "'bioschemas:encodesBioChemEntity" in all props
        self.assertIn("bioschemas:encodesBioChemEntity", all_prop_names)
        all_props = self.se.list_all_defined_properties()
        all_prop_names = [_prop.name for _prop in all_props]
        self.assertEqual(["bioschemas:encodesBioChemEntity"], all_prop_names)

    def test_get_class(self):
        """Test get_class function"""
        scls = self.se.get_class("bioschemas:Gene")
        self.assertEqual(SchemaClass, type(scls))

    def test_get_property(self):
        """Test get_property function"""
        sp = self.se.get_property("bioschemas:encodesBioChemEntity")
        self.assertEqual(SchemaProperty, type(sp))
        self.assertIn("schema:Text", [_cls.name for _cls in sp.range])


if __name__ == "__main__":
    unittest.main()
