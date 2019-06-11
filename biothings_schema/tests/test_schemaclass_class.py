import unittest

from biothings_schema import Schema
from biothings_schema import SchemaClass


class TestSchemaClassClass(unittest.TestCase):
    """Test SchemaClass Class
    """
    def setUp(self):
        schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'
        self.se = Schema(schema_url)

    def test_initialization(self):
        # if input class is not in schema, should raise ValueError
        with self.assertRaises(ValueError) as cm:
            SchemaClass('ttt', self.se)
        self.assertEqual(
            'Class ttt is not defined in Schema. Could not access it',
            str(cm.exception)
        )

    def test_parent_classes(self):
        """ Test parent_classes function
        """
        scls = self.se.get_class("Gene")
        parents = scls.parent_classes
        # check the first item of should be 'Thing'
        self.assertEqual(parents[0][0].name, 'Thing')
        # if input is the root class, should return empty list
        scls = self.se.get_class("Thing")
        parents = scls.parent_classes
        self.assertEqual(parents, [])

    def test_descendant_classes(self):
        """ Test descendant_classes function"""
        scls = self.se.get_class("MolecularEntity")
        descendants = scls.descendant_classes
        descendant_names = [_item.name for _item in descendants]
        # check if gene is in descendants
        self.assertIn('Gene', descendant_names)
        # check if Thing is in descendants (Thing is its parent classs)
        self.assertNotIn('Thing', descendant_names)
        # check itself should not in descendants
        self.assertNotIn('MolecularEntity', descendant_names)
        # test if input class is the leaf class
        scls = self.se.get_class("Gene")
        descendants = scls.descendant_classes
        self.assertEqual(descendants, [])

    def test_child_classes(self):
        """ Test child_classes function"""
        scls = self.se.get_class("MolecularEntity")
        children = scls.child_classes
        children_names = [_item.name for _item in children]
        # check if GeneFamily is in children
        self.assertIn('GeneFamily', children_names)
        # check if gene is in children (gene is descendant)
        self.assertNotIn('Gene', children_names)
        # check if Thing is in children (Thing is its parent classs)
        self.assertNotIn('Thing', children_names)
        # check itself should not in children
        self.assertNotIn('MolecularEntity', children_names)
        # test if input class is the leaf class
        scls = self.se.get_class("Gene")
        children = scls.children_classes
        self.assertEqual(children, [])





if __name__ == '__main__':
    unittest.main()
