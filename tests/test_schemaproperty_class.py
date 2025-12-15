import unittest

from biothings_schema import Schema, SchemaProperty


class TestSchemaPropertyClass(unittest.TestCase):
    """Test SchemaProperty Class"""

    def setUp(self):
        schema_url = "https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld"
        self.se = Schema(schema_url)
        # test response if input is NAME only
        sp = self.se.get_property("ensembl")
        self.assertEqual(sp.name, "bts:ensembl")
        self.assertEqual(sp.uri, "http://schema.biothings.io/ensembl")
        self.assertEqual(sp.label, "ensembl")
        # test response if input is CURIE only
        sp = self.se.get_property("bts:ensembl")
        self.assertEqual(sp.name, "bts:ensembl")
        self.assertEqual(sp.uri, "http://schema.biothings.io/ensembl")
        self.assertEqual(sp.label, "ensembl")
        # test response if input is URI only
        sp = self.se.get_property("http://schema.biothings.io/ensembl")
        self.assertEqual(sp.name, "bts:ensembl")
        self.assertEqual(sp.uri, "http://schema.biothings.io/ensembl")
        self.assertEqual(sp.label, "ensembl")

    def test_initialization(self):
        # if input property is not in schema, defined_in_schema should be False
        sp = SchemaProperty("dd", self.se)
        self.assertFalse(sp.defined_in_schema)

    def test_parent_properties(self):
        """Test parent_properties function"""
        sp = self.se.get_property("ensembl")
        parents = sp.parent_properties
        # check the first item of should be 'Thing'
        self.assertIn("schema:identifier", [_item.name for _item in parents])
        # check negative cases
        self.assertNotIn("bts:sgd", [_item.name for _item in parents])
        # if input doesn't have parent properties, should return empty list
        sp = self.se.get_property("identifier")
        # Handle case where get_property returns a list
        if isinstance(sp, list):
            sp = sp[0]  # Use the first property if multiple are found
        parents = sp.parent_properties
        self.assertEqual(parents, [])
        # test if input is not defined
        sp = self.se.get_property("dd")
        parents = sp.parent_properties
        self.assertEqual(parents, [])

    def test_child_properties(self):
        """Test child_properties function"""
        sp = self.se.get_property("identifier")
        # Handle case where get_property returns a list
        if isinstance(sp, list):
            sp = sp[0]  # Use the first property if multiple are found
        children = sp.child_properties
        child_names = [_item.name for _item in children]
        # check if ensembl is in descendants
        self.assertIn("bts:ensembl", child_names)
        # check if affectsExpressionOf is in descendants
        self.assertNotIn("bts:affectsExpressionOf", child_names)
        # check itself should not in descendants
        self.assertNotIn("schema:identifier", child_names)
        # test if input property is the leaf property
        sp = self.se.get_property("ensembl")
        children = sp.child_properties
        self.assertEqual(children, [])
        # test if input is not defined
        sp = self.se.get_property("dd")
        children = sp.child_properties
        self.assertEqual(children, [])

    def test_describe(self):
        """test describe function"""
        sp = self.se.get_property("dd")
        describe = sp.describe()
        self.assertEqual(describe, {})


if __name__ == "__main__":
    unittest.main()
