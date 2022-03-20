import os.path
import unittest

from biothings_schema import Schema, SchemaClass, SchemaProperty

_CURRENT = os.path.abspath(os.path.dirname(__file__))


class TestSchemaClass(unittest.TestCase):
    """Test Schema Validator Class
    """
    def setUp(self):
        schema_file = os.path.join(
            _CURRENT, 'data', 'extend_from_bioschemas.json'
        )
        self.se = Schema(schema_file)

    def test_list_all_classes(self):
        """ Test list_all_classes function
        """
        all_cls = self.se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]
        # assert root level Class in all classes
        self.assertIn('bioschemas:Gene', all_cls_names)
        # class name should be curie
        self.assertNotIn('Gene', all_cls_names)
        # assert type of the class is SchemaClass
        self.assertEqual(SchemaClass, type(all_cls[0]))

    def test_list_all_properties(self):
        """ Test list_all_properties function"""
        all_props = self.se.list_all_properties()
        all_prop_names = [_prop.name for _prop in all_props]
        # assert "name" in all props
        self.assertIn('schema:name', all_prop_names)
        # property name should be curie
        self.assertNotIn('name', all_prop_names)
        # assert "ffff" should not be one of the props
        self.assertNotIn('bts:ffff', all_prop_names)
        # assert type of the property is SchemaProperty
        self.assertEqual(SchemaProperty, type(all_props[0]))

    def test_get_class(self):
        """ Test get_class function"""
        scls = self.se.get_class("bioschemas:Gene")
        self.assertEqual(SchemaClass, type(scls))

    def test_get_property(self):
        """ Test get_property function"""
        sp = self.se.get_property("bioschemas:encodesBioChemEntity")
        self.assertEqual(SchemaProperty, type(sp))


if __name__ == '__main__':
    unittest.main()
