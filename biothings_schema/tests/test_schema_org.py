import unittest

from biothings_schema import Schema


class TestSchemaOrg(unittest.TestCase):
    """Using SchemaOrg Schema to test all functions in biothings_schema
    """
    def setUp(self):
        # preload schemaorg schema
        self.se = Schema()
        # test list_all_classes
        self.clses = self.se.list_all_classes()
        # test list_all_properties
        self.props = self.se.list_all_properties()

    def test_schemaclass_class(self):
        """ Test the SchemaClass Class using all classes in Schemaorg schema"""
        # loop through all classes
        for _cls in self.clses:
            # test get_class
            scls = self.se.get_class(_cls.name)
            # test description function
            description = scls.description
            # test ancestor function
            ancestor = scls.ancestor_classes
            # test parent_classes function
            parent = scls.parent_classes
            # test child_classes function
            children = scls.child_classes
            # test descendant_classes function
            descendant = scls.descendant_classes
            # test list_properties function
            properties = scls.list_properties()
            properties = scls.list_properties(group_by_class=False)
            properties = scls.list_properties(class_specific=False)
            properties = scls.list_properties(group_by_class=False,
                                              class_specific=False)
            # test used_by function
            usage = scls.used_by()
            # test describe function
            describe = scls.describe()

    def test_schemaproperty_class(self):
        """ Test the SchemaProperty Class using all classes in Schemaorg schema
        """
        # loop through all properties
        for _prop in self.props:
            # test get_property
            sp = self.se.get_property(_prop.name)
            # test description function
            description = sp.description
            # test parent_classes function
            parent = sp.parent_properties
            # test child_classes function
            children = sp.child_properties
            # test descendant_classes function
            descendant = sp.descendant_properties
            # test describe function
            describe = sp.describe()


if __name__ == '__main__':
    unittest.main()
