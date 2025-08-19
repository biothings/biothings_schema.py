import unittest
import os.path

from biothings_schema import Schema, SchemaClass, SchemaProperty


_CURRENT = os.path.abspath(os.path.dirname(__file__))


class TestSchemaClass(unittest.TestCase):
    def setUp(self):
        d2h_schema_file = os.path.join(
            _CURRENT, "data", "data2file_schema.jsonld"
        )
        biosample_schema_file = os.path.join(
            _CURRENT, "data", "biosample_schema.json"
        )
        self.d2h_se = Schema(d2h_schema_file)
        self.bio_se = Schema(biosample_schema_file)

    def test_list_all_classes(self):
        """Test list_all_classes function"""
        all_cls = self.d2h_se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]

        # Root-level CURIE class is included
        self.assertIn(
            "bts:PlanetaryEntity",
            all_cls_names,
            "'bts:PlanetaryEntity' not found in class names",
        )
        # Raw label name is NOT present
        self.assertNotIn(
            "Gene",
            all_cls_names,
            "'Gene' (non-CURIE) unexpectedly found in class names",
        )
        # All classes are SchemaClass instances
        for cls in all_cls:
            self.assertIsInstance(
                cls, SchemaClass, "Not all classes are SchemaClass instances"
            )

    def test_list_all_properties(self):
        """Test list_all_properties function"""
        all_props = self.d2h_se.list_all_properties()
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

        self.assertGreater(
            len(all_props), 0, "No properties returned"
        )
        self.assertIsInstance(
            all_props[0],
            SchemaProperty,
            "First property is not a SchemaProperty"
        )

    def test_get_class(self):
        """Test get_class function"""
        scls = self.d2h_se.get_class("bts:Gene")
        self.assertIsInstance(
            scls, SchemaClass, "Returned class is not a SchemaClass"
        )

    def test_get_property(self):
        """Test get_property function"""
        sp = self.d2h_se.get_property("bts:geneticallyInteractsWith")
        self.assertIsInstance(
            sp, SchemaProperty, "Returned property is not a SchemaProperty"
        )

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
        scls = self.bio_se.get_class("BioSample")
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
