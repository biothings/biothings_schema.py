import unittest

from biothings_schema.curies import CurieUriConverter

CONTEXT = {
    "schema": "http://schema.org/",
    "bts": "http://discovery.biothings.io/bts/",
    "schema1": "http://schema.org",
}

URI_LIST = [
    "http://schema.org/Person",
    "http://discovery.biothings.io/bts/Gene",
    "schema:Drug",
    "http://schema.org/Gene",
]


class TestCurieUriConverter(unittest.TestCase):
    """Test CurieUriConverter Class"""

    def setUp(self):
        self.converter = CurieUriConverter(CONTEXT, URI_LIST)

    def test_determine_id_type(self):
        """Test determine_id_type function"""
        self.assertEqual(self.converter.determine_id_type("schema:Gene"), "curie")
        self.assertEqual(self.converter.determine_id_type("http://schema.org/Gene"), "url")
        self.assertEqual(self.converter.determine_id_type("Gene"), "name")
        self.assertEqual(self.converter.determine_id_type("schema:Gene:Gene"), "name")

    def test_get_uri(self):
        """Test get_uri function"""
        self.assertEqual(self.converter.get_uri("schema:Thing"), "http://schema.org/Thing")
        self.assertEqual(self.converter.get_uri("schema2:Thing"), "schema2:Thing")
        self.assertEqual(self.converter.get_uri("schema1:Thing"), "http://schema.org/Thing")
        self.assertEqual(self.converter.get_uri("Thing"), "Thing")
        self.assertEqual(self.converter.get_uri("Person"), "http://schema.org/Person")
        self.assertEqual(
            set(self.converter.get_uri("Gene")),
            set(["http://discovery.biothings.io/bts/Gene", "http://schema.org/Gene"]),
        )
        self.assertEqual(self.converter.get_uri("Drug"), "schema:Drug")

    def test_get_curie(self):
        """Test get_curie function"""
        self.assertEqual(self.converter.get_curie("http://schema.org/Thing"), "schema:Thing")
        self.assertEqual(set(self.converter.get_curie("Gene")), set(["bts:Gene", "schema:Gene"]))
        self.assertEqual(self.converter.get_curie("schema:Thing"), "schema:Thing")
        self.assertEqual(self.converter.get_curie("Person"), "schema:Person")

    def test_get_label(self):
        """Test get_label function"""
        self.assertEqual(self.converter.get_label("http://schema.org/Thing"), "Thing")
        self.assertEqual(self.converter.get_label("Thing"), "Thing")
        self.assertEqual(self.converter.get_label("schema:Thing"), "Thing")


if __name__ == "__main__":
    unittest.main()
