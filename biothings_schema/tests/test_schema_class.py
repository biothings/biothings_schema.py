import unittest

from biothings_schema import Schema
from biothings_schema import SchemaClass
from biothings_schema import SchemaProperty


class TestSchemaClass(unittest.TestCase):
    """Test Schema Validator Class
    """
    def setUp(self):
        schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'
        self.se = Schema(schema_url)

    def test_list_all_classes(self):
        """ Test list_all_classes function
        """
        all_cls = self.se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]
        # assert root level Class in all classes
        self.assertIn('Thing', all_cls_names)
        # assert class "Gene" in all classes
        self.assertIn('Gene', all_cls_names)
        # class 'ffff' should not be one of the classes
        self.assertNotIn('ffff', all_cls_names)
        # assert type of the class is SchemaClass
        self.assertEqual(SchemaClass, type(all_cls[0]))

    def test_get_class(self):
        """ Test get_class function"""
        scls = self.se.get_class("Gene")
        self.assertEqual(SchemaClass, type(scls))

    def test_get_property(self):
        """ Test get_property function"""
        sp = self.se.get_property("ensembl")
        self.assertEqual(SchemaProperty, type(sp))


if __name__ == '__main__':
    unittest.main()
