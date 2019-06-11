import unittest

from biothings_schema import Schema
from biothings_schema import SchemaProperty


class TestSchemaPropertyClass(unittest.TestCase):
    """Test SchemaProperty Class
    """
    def setUp(self):
        schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'
        self.se = Schema(schema_url)

    def test_initialization(self):
        # if input class is not in schema, should raise ValueError
        with self.assertRaises(ValueError) as cm:
            SchemaProperty('ttt', self.se)
        self.assertEqual(
            'Property ttt is not defined in Schema. Could not access it',
            str(cm.exception)
        )

    def test_parent_properties(self):
        """ Test parent_properties function
        """
        sp = self.se.get_property("ensembl")
        parents = sp.parent_properties
        # check the first item of should be 'Thing'
        self.assertIn("identifier", [_item.name for _item in parents])
        # check negative cases
        self.assertNotIn("sgd", [_item.name for _item in parents])
        # if input doesn't have parent properties, should return empty list
        sp = self.se.get_property("identifier")
        parents = sp.parent_properties
        self.assertEqual(parents, [])

    def test_child_properties(self):
        """ Test child_properties function"""
        sp = self.se.get_property("identifier")
        children = sp.child_properties
        child_names = [_item.name for _item in children]
        # check if ensembl is in descendants
        self.assertIn('ensembl', child_names)
        # check if affectsExpressionOf is in descendants
        self.assertNotIn('affectsExpressionOf', child_names)
        # check itself should not in descendants
        self.assertNotIn('identifier', child_names)
        # test if input property is the leaf property
        sp = self.se.get_property("ensembl")
        children = sp.child_properties
        self.assertEqual(children, [])


if __name__ == '__main__':
    unittest.main()
