import unittest
from unittest.mock import MagicMock, patch

import requests

from biothings_schema import Schema
from biothings_schema.dataload import get_latest_schemaorg_version, get_schemaorg_version
from biothings_schema.settings import SCHEMAORG_DEFAULT_VERSION


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
        """Test the SchemaProperty Class using all classes in Schemaorg schema"""
        # loop through all properties
        for _prop in self.props:
            # test get_property
            sp = self.se.get_property(_prop.name)
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


class TestGetSchemaorgVersion(unittest.TestCase):
    """Test schema.org release tag parsing and fallback behavior."""

    def setUp(self):
        get_latest_schemaorg_version.cache_clear()

    def tearDown(self):
        get_latest_schemaorg_version.cache_clear()

    def test_get_latest_schemaorg_version(self):
        """Live call: get_latest_schemaorg_version() returns a valid version string."""
        version = get_latest_schemaorg_version()
        self.assertRegex(version, r"^\d+\.\d+$")

    def test_get_schemaorg_version(self):
        """Live call: get_schemaorg_version() returns a valid version string."""
        version = get_schemaorg_version()
        self.assertRegex(version, r"^\d+\.\d+$")

    # The following tests require mocking since we need to simulate
    # edge cases that cannot be reproduced with a live API call.

    @patch("biothings_schema.dataload.requests.get")
    def test_tag_with_release_suffix(self, mock_get):
        """Old tag format v13.0-release is still parsed correctly."""
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = {"tag_name": "v13.0-release"}
        self.assertEqual(get_latest_schemaorg_version(), "13.0")

    @patch("biothings_schema.dataload.requests.get")
    def test_unrecognized_tag_raises_value_error(self, mock_get):
        """Unrecognized tag format raises ValueError."""
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = {"tag_name": "something-weird"}
        with self.assertRaises(ValueError):
            get_latest_schemaorg_version()

    @patch("biothings_schema.dataload.requests.get", side_effect=requests.exceptions.Timeout)
    def test_timeout_falls_back_to_default(self, _):
        """Network timeout falls back to default version."""
        self.assertEqual(get_schemaorg_version(), SCHEMAORG_DEFAULT_VERSION)

    @patch("biothings_schema.dataload.requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_connection_error_falls_back_to_default(self, _):
        """Connection error falls back to default version."""
        self.assertEqual(get_schemaorg_version(), SCHEMAORG_DEFAULT_VERSION)


if __name__ == "__main__":
    unittest.main()
