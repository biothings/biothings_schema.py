import unittest

from biothings_schema import Schema


class TestSchemaOrg(unittest.TestCase):
    """Using SchemaOrg Schema to test all functions in biothings_schema"""

    def setUp(self):
        # preload schemaorg-only schema
        self.se = Schema(base_schema=["schema.org"])
        # test list_all_classes
        self.clses = self.se.list_all_classes()
        # test list_all_properties
        self.props = self.se.list_all_properties()

    def test_schemaclass_class(self):
        """Test the SchemaClass Class using all classes in Schemaorg schema"""
        # loop through all classes
        for _cls in self.clses:
            # test get_class
            scls = self.se.get_class(_cls.name)
            self.assertEqual(scls.prefix, "schema")
            # test describe function
            describe = scls.describe()
            scls = self.se.get_class(_cls.name, output_type="curie")
            describe = scls.describe()
            scls = self.se.get_class(_cls.name, output_type="uri")
            describe = scls.describe()
            scls = self.se.get_class(_cls.name, output_type="label")
            describe = scls.describe()
            del describe

    def test_schemaproperty_class(self):
        """Test the SchemaProperty Class using first 10 properties in Schemaorg schema"""
        # loop through first 10 properties
        for _prop in self.props[:100]:
            # test get_property
            sp = self.se.get_property(_prop.name)
            # Skip properties from external namespaces or standard RDF/RDFS properties
            if sp.prefix is None or sp.prefix in ['rdfs', 'rdf', 'xsd', 'bibo', 'brick']:
                continue
            self.assertEqual(sp.prefix, "schema")
            # test describe function
            describe = sp.describe()
            sp = self.se.get_property(_prop.name, output_type="curie")
            # test describe function
            describe = sp.describe()
            sp = self.se.get_property(_prop.name, output_type="uri")
            # test describe function
            describe = sp.describe()
            sp = self.se.get_property(_prop.name, output_type="label")
            # test describe function
            describe = sp.describe()
            del describe


if __name__ == "__main__":
    unittest.main()
