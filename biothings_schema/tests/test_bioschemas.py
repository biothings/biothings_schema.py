import unittest

from biothings_schema import Schema, SchemaClass, SchemaProperty

SCHEMA_URL = (
    "https://raw.githubusercontent.com/data2health/schemas/biothings/"
    "biothings/biothings_curie_kevin.jsonld"
)


def load_schema(path_or_url: str) -> Schema:
    """Create a Schema from a file path or URL."""
    return Schema(path_or_url)



class TestSchemaBasics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.se = load_schema(SCHEMA_URL)


    def test_list_all_classes(self):
        """Test list_all_classes function"""
        all_cls = self.se.list_all_classes()
        all_cls_names = [_cls.name for _cls in all_cls]

        # Root-level CURIE class is included
        self.assertIn("bts:PlanetaryEntity", all_cls_names,
                        "'bts:PlanetaryEntity' not found in class names")
        # Raw label name is NOT present
        self.assertNotIn("Gene", all_cls_names,
                            "'Gene' (non-CURIE) unexpectedly found in class names")
        # All classes are SchemaClass instances
        for cls in all_cls:
            self.assertIsInstance(cls, SchemaClass,
                                    "Not all classes are SchemaClass instances")


    def test_list_all_properties(self):
        """Test list_all_properties function"""
        all_props = self.se.list_all_properties()
        all_prop_names = [_prop.name for _prop in all_props]

        self.assertIn("schema:author", all_prop_names,
                        "'schema:author' not found in properties")
        self.assertNotIn("name", all_prop_names,
                            "Unexpected plain 'name' found in properties")
        self.assertNotIn("bts:ffff", all_prop_names,
                            "Fake property 'bts:ffff' should not exist")

        self.assertGreater(len(all_props), 0, "No properties returned")
        self.assertIsInstance(all_props[0], SchemaProperty,
                                "First property is not a SchemaProperty")


    def test_get_class(self):
        """Test get_class function"""
        scls = self.se.get_class("bts:Gene")
        self.assertIsInstance(scls, SchemaClass, 
                            "Returned class is not a SchemaClass")


    def test_get_property(self):
        """Test get_property function"""
        sp = self.se.get_property("bts:geneticallyInteractsWith")
        self.assertIsInstance(sp, SchemaProperty,
                            "Returned property is not a SchemaProperty")
