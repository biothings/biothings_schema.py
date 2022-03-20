import os
import unittest

from biothings_schema import Schema
from biothings_schema.base import load_json_or_yaml


_CURRENT = os.path.abspath(os.path.dirname(__file__))


class TestSchemaClassClass(unittest.TestCase):
    """Test SchemaClass Class
    """
    def setUp(self):
        schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'
        self.se = Schema(schema_url)

    def test_initialization_with_context_works(self):
        biothings_jsonld_path = os.path.join(_CURRENT,
                                             'data',
                                             'biothings_test.jsonld')
        schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'
        biothings_schema = load_json_or_yaml(biothings_jsonld_path)
        self.se_with_context = Schema(schema_url, biothings_schema['@context'])
        self.assertEqual(self.se_with_context.schema, self.se.schema)

    def test_initialization(self):
        # if input class is not in schema, defined_in_schema should be False
        scls = self.se.get_class("dd")
        self.assertFalse(scls.defined_in_schema)
        # test response if input is NAME only
        scls = self.se.get_class("bts:Gene")
        self.assertEqual(scls.name, "bts:Gene")
        self.assertEqual(scls.uri, "http://schema.biothings.io/Gene")
        self.assertEqual(scls.label, "Gene")
        # test response if input is CURIE only
        scls = self.se.get_class("bts:Gene")
        self.assertEqual(scls.name, "bts:Gene")
        self.assertEqual(scls.uri, "http://schema.biothings.io/Gene")
        self.assertEqual(scls.label, "Gene")
        # test response if input is URI only
        scls = self.se.get_class("http://schema.biothings.io/Gene")
        self.assertEqual(scls.name, "bts:Gene")
        self.assertEqual(scls.uri, "http://schema.biothings.io/Gene")
        self.assertEqual(scls.label, "Gene")

    def test_parent_classes(self):
        """ Test parent_classes function
        """
        scls = self.se.get_class("bts:Gene")
        parents = scls.parent_classes
        # check the first item of should be 'Thing'
        self.assertEqual(parents[0][0].name, 'schema:Thing')
        # if input is the root class, should return empty list
        scls = self.se.get_class("Thing")
        parents = scls.parent_classes
        self.assertEqual(parents, [])
        # check the response if class not exist
        scls = self.se.get_class("dd")
        parents = scls.parent_classes
        self.assertEqual(parents, [])
        ###############################
        # test if output_type is uri
        scls = self.se.get_class("bts:Gene", output_type="uri")
        parents = scls.parent_classes
        # check the first item of should be 'Thing'
        self.assertEqual(parents[0][0], 'http://schema.org/Thing')
        ###############################
        # test if output_type is label
        scls = self.se.get_class("bts:Gene", output_type="label")
        parents = scls.parent_classes
        # check the first item of should be 'Thing'
        self.assertEqual(parents[0][0], 'Thing')
        ###############################
        # test if output_type is curie
        scls = self.se.get_class("bts:Gene", output_type="curie")
        parents = scls.parent_classes
        # check the first item of should be 'Thing'
        self.assertEqual(parents[0][0], 'schema:Thing')

    def test_ancestor_classes(self):
        """ Test ancestor_classes function"""
        ###############################
        # test if output_type is python class
        scls = self.se.get_class("bts:MolecularEntity")
        ancestors = scls.ancestor_classes
        ancestor_names = [_item.name for _item in ancestors]
        # check if gene is in ancestors
        self.assertIn('schema:Thing', ancestor_names)
        self.assertIn('bts:BiologicalEntity', ancestor_names)
        # check if Gene is in ancestors (Gene is its child classs)
        self.assertNotIn('bts:Gene', ancestor_names)
        # check itself should not in ancestors
        self.assertNotIn('bts:MolecularEntity', ancestor_names)
        # test if input class is the root class
        scls = self.se.get_class("Thing")
        self.assertEqual(scls.ancestor_classes, [])
        # test if input class not exists
        scls = self.se.get_class("dd")
        self.assertEqual(scls.ancestor_classes, [])
        ###############################
        # test if output_type is curie
        scls = self.se.get_class("bts:MolecularEntity", output_type="curie")
        ancestors = scls.ancestor_classes
        # check if BiologicalEntity is in descendants
        self.assertIn('bts:BiologicalEntity', ancestors)
        self.assertIn('schema:Thing', ancestors)
        ###############################
        # test if output_type is label
        scls = self.se.get_class("bts:MolecularEntity", output_type="label")
        ancestors = scls.ancestor_classes
        # check if Thing is in ancestors
        self.assertIn('Thing', ancestors)
        self.assertIn('BiologicalEntity', ancestors)
        ###############################
        # test if output_type is uri
        scls = self.se.get_class("bts:MolecularEntity", output_type="uri")
        ancestors = scls.ancestor_classes
        # check if gene is in descendants
        self.assertIn('http://schema.biothings.io/BiologicalEntity',
                      ancestors)
        self.assertIn('http://schema.org/Thing',
                      ancestors)

    def test_descendant_classes(self):
        """ Test descendant_classes function"""
        ###############################
        # test if output_type is python class
        scls = self.se.get_class("bts:MolecularEntity")
        descendants = scls.descendant_classes
        descendant_names = [_item.name for _item in descendants]
        # check if gene is in descendants
        self.assertIn('bts:Gene', descendant_names)
        # check if Thing is in descendants (Thing is its parent classs)
        self.assertNotIn('schema:Thing', descendant_names)
        # check itself should not in descendants
        self.assertNotIn('bts:MolecularEntity', descendant_names)
        # test if input class is the leaf class
        scls = self.se.get_class("bts:Gene")
        descendants = scls.descendant_classes
        self.assertEqual(descendants, [])
        # test if input class not exists
        scls = self.se.get_class("dd")
        descendants = scls.descendant_classes
        self.assertEqual(descendants, [])
        ###############################
        # test if output_type is curie
        scls = self.se.get_class("bts:MolecularEntity", output_type="curie")
        descendants = scls.descendant_classes
        # check if gene is in descendants
        self.assertIn('bts:Gene', descendants)
        ###############################
        # test if output_type is label
        scls = self.se.get_class("bts:MolecularEntity", output_type="label")
        descendants = scls.descendant_classes
        # check if gene is in descendants
        self.assertIn('Gene', descendants)
        ###############################
        # test if output_type is uri
        scls = self.se.get_class("bts:MolecularEntity", output_type="uri")
        descendants = scls.descendant_classes
        # check if gene is in descendants
        self.assertIn('http://schema.biothings.io/Gene', descendants)

    def test_child_classes(self):
        """ Test child_classes function"""
        ###############################
        # test if output_type is python class
        scls = self.se.get_class("bts:MolecularEntity")
        children = scls.child_classes
        children_names = [_item.name for _item in children]
        # check if GeneFamily is in children
        self.assertIn('bts:GeneFamily', children_names)
        # check if gene is in children (gene is descendant)
        self.assertNotIn('bts:Gene', children_names)
        # check if Thing is in children (Thing is its parent classs)
        self.assertNotIn('schema:Thing', children_names)
        # check itself should not in children
        self.assertNotIn('bts:MolecularEntity', children_names)
        # test if input class is the leaf class
        scls = self.se.get_class("bts:Gene")
        children = scls.child_classes
        self.assertEqual(children, [])
        # test if input class is not defined
        scls = self.se.get_class("dd")
        children = scls.child_classes
        self.assertEqual(children, [])
        ###############################
        # test if output_type is curie
        scls = self.se.get_class("bts:MolecularEntity", output_type="curie")
        children = scls.child_classes
        # check if GeneFamily is in children
        self.assertIn('bts:GeneFamily', children)
        ###############################
        # test if output_type is uri
        scls = self.se.get_class("bts:MolecularEntity", output_type="uri")
        children = scls.child_classes
        # check if GeneFamily is in children
        self.assertIn('http://schema.biothings.io/GeneFamily', children)
        ###############################
        # test if output_type is label
        scls = self.se.get_class("bts:MolecularEntity", output_type="label")
        children = scls.child_classes
        # check if GeneFamily is in children
        self.assertIn('GeneFamily', children)

    def test_used_by(self):
        """ Test used_by function"""
        scls = self.se.get_class("bts:GenomicEntity")
        usage = scls.used_by()
        self.assertTrue(len(usage) > 1)
        self.assertEqual(list, type(usage))
        # test if class is not defined
        scls = self.se.get_class("dd")
        usage = scls.used_by()
        self.assertEqual(usage, [])

    def test_describe(self):
        """test describe function"""
        scls = self.se.get_class("dd")
        describe = scls.describe()
        self.assertEqual(describe, {})


if __name__ == '__main__':
    unittest.main()
