import unittest
import os.path

from biothings_schema import Schema, SchemaClass, SchemaProperty


_CURRENT = os.path.abspath(os.path.dirname(__file__))


class TestSchemaClass(unittest.TestCase):
    def setUp(self):
        ext_bs_schema_file = os.path.join(
            _CURRENT, "data", "extend_from_bioschemas.json"
        )
        biosample_schema_file = os.path.join(
            _CURRENT, "data", "biosample_schema.json"
        )
        self.ext_bs_se = Schema(ext_bs_schema_file)
        self.bio_se = Schema(biosample_schema_file)

    def test_list_all_classes(self):
        """Test list_all_classes function"""
        all_cls = self.ext_bs_se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]
        # assert root level Class in all classes
        self.assertIn("bioschemas:Gene", all_cls_names)
        # class name should be curie
        self.assertNotIn("Gene", all_cls_names)
        # assert type of the class is SchemaClass
        self.assertEqual(SchemaClass, type(all_cls[0]))

    def test_list_all_properties(self):
        """Test list_all_properties function"""
        all_props = self.ext_bs_se.list_all_properties()
        all_prop_names = [_prop.name for _prop in all_props]
        # assert "name" in all props
        self.assertIn("schema:name", all_prop_names)
        # property name should be curie
        self.assertNotIn("name", all_prop_names)
        # assert "ffff" should not be one of the props
        self.assertNotIn("bts:ffff", all_prop_names)
        # assert type of the property is SchemaProperty
        self.assertEqual(SchemaProperty, type(all_props[0]))

    def test_get_class(self):
        """Test get_class function"""
        scls = self.ext_bs_se.get_class("bioschemas:Gene")
        self.assertEqual(SchemaClass, type(scls))

    def test_get_property(self):
        """Test get_property function"""
        sp = self.ext_bs_se.get_property("bioschemas:encodesBioChemEntity")
        self.assertEqual(SchemaProperty, type(sp))

    def test_list_all_classes_multi_class(self):
        """Test list_all_classes function"""
        all_cls = self.bio_se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]
        # Assert root-level CURIE class is included
        self.assertIn(
            "schema:BioChemEntity",
            all_cls_names,
            "'schema:BioChemEntity' not found in class names",
        )
        # Assert raw label name is NOT present
        self.assertNotIn(
            "Gene",
            all_cls_names,
            "'Gene' (non-CURIE) unexpectedly found in class names",
        )
        # Assert all classes are SchemaClass instances
        for cls in all_cls:
            self.assertIsInstance(
                cls, SchemaClass, "Not all classes are SchemaClass instances"
            )

    def test_list_all_properties_multi_class(self):
        """Local test of list_all_properties function"""
        all_props = self.bio_se.list_all_properties()
        all_prop_names = [_prop.name for _prop in all_props]

        self.assertIn(
            "schema:author",
            all_prop_names,
            "'schema:author' not found in properties",
        )
        self.assertNotIn(
            "name",
            all_prop_names,
            "Unexpected plain 'name' found in properties",
        )
        self.assertNotIn(
            "bts:ffff",
            all_prop_names,
            "Fake property 'bts:ffff' should not exist",
        )
        self.assertIsInstance(
            all_props[0],
            SchemaProperty,
            "First property is not a SchemaProperty"
        )

    def test_get_class_multi_class(self):
        """Local test of get_class function"""
        scls = self.bio_se.get_class("bioschemastypesdrafts:BioSample")
        self.assertIsInstance(
            scls, SchemaClass, "Returned class is not a SchemaClass"
        )

    def test_get_property_multi_class(self):
        """Local test of get_property function"""
        sp = self.bio_se.get_property(
            "bioschemastypesdrafts:anatomicalStructure"
        )
        self.assertIsInstance(
                sp, SchemaProperty, "Returned property is not a SchemaProperty"
        )
