import os
import sys
import unittest

from biothings_schema import Schema, SchemaValidationError, SchemaValidator
from biothings_schema.dataload import load_json_or_yaml

_CURRENT = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.join(_CURRENT, os.pardir, os.pardir)
sys.path.append(_ROOT)


class TestSchemaValidator(unittest.TestCase):
    """Test Schema Validator Class"""

    def setUp(self):
        biothings_jsonld_path = os.path.join(_CURRENT, "data", "biothings_test.jsonld")
        biothings_schema = load_json_or_yaml(biothings_jsonld_path)
        schema_nx = Schema(biothings_schema)
        self.sv = SchemaValidator(biothings_schema, schema_nx)
        biothings_duplicate = os.path.join(_CURRENT, "data", "biothings_duplicate_test.jsonld")
        duplicate_schema = load_json_or_yaml(biothings_duplicate)
        self.sv_duplicate = SchemaValidator(duplicate_schema, schema_nx)

        # Load mock schema for testing recursive parent validation merging
        mock_schema_path = os.path.join(_CURRENT, "data", "mock_multi-inheritance_schema.jsonld")
        self.mock_schema = load_json_or_yaml(mock_schema_path)
        mock_schema_nx = Schema(self.mock_schema)
        self.mock_sv = SchemaValidator(self.mock_schema, mock_schema_nx)

    def test_validate_class_label(self):
        """Test validate_class_label function"""
        with self.assertRaises(SchemaValidationError):
            self.sv.validate_class_label("http://schema.biothings.io/kkk")
        try:
            self.sv.validate_class_label("http://schema.biothings.io/Kk")
        except SchemaValidationError:
            self.fail("validate_class_label raised Exception unexpectly!")

    def test_validate_property_label(self):
        """Test validate_property_label function"""
        with self.assertRaises(SchemaValidationError):
            self.sv.validate_property_label("http://schema.biothings.io/Kkk")
        try:
            self.sv.validate_property_label("http://schema.biothings.io/kk")
        except SchemaValidationError:
            self.fail("validate_property_label raised Exception unexpectly!")

    def test_validate_subclassof_field(self):
        """Test validate_subclassof_field function"""
        test_single_input_fail = {"@id": "http://schema.biothings.io/Kk"}
        test_list_input_fail = [
            {"@id": "http://schema.biothings.io/Case"},
            {"@id": "http://schema.biothings.io/Kk"},
        ]
        test_single_input_success = {"@id": "http://schema.biothings.io/Case"}
        test_list_input_success = [
            {"@id": "http://schema.biothings.io/Case"},
            {"@id": "http://schema.biothings.io/Drug"},
        ]
        with self.assertRaises(SchemaValidationError):
            self.sv.validate_subclassof_field(test_single_input_fail)
        with self.assertRaises(SchemaValidationError):
            self.sv.validate_subclassof_field(test_list_input_fail)
        try:
            self.sv.validate_subclassof_field(test_single_input_success)
        except SchemaValidationError:
            self.fail("validate_subclassof_field raise Exception unexpectly")
        try:
            self.sv.validate_subclassof_field(test_list_input_success)
        except SchemaValidationError:
            self.fail("validate_subclassof_field raise Exception unexpectly")

    def test_validate_domainincludes_field(self):
        """Test validate_domainincludes_field function"""
        test_single_input_fail = {"@id": "http://schema.biothings.io/Kk"}
        test_list_input_fail = [
            {"@id": "http://schema.biothings.io/Case"},
            {"@id": "http://schema.biothings.io/Kk"},
        ]
        test_single_input_success = {"@id": "http://schema.biothings.io/Case"}
        test_list_input_success = [
            {"@id": "http://schema.biothings.io/Case"},
            {"@id": "http://schema.biothings.io/Drug"},
        ]

        # test missing domainIncludes
        self.sv.validate_domainIncludes_field(test_single_input_fail)
        err = self.sv.validation_errors[-1]
        self.assertTrue(isinstance(err, SchemaValidationError))
        self.assertTrue(err.warning)  # missing domainIncludes should just a warning
        self.assertEqual(err.record_id, test_single_input_fail["@id"])

        # test single or multiple domainIncludes values
        record = {"@id": "testClass"}
        with self.assertRaises(SchemaValidationError):
            record["http://schema.org/domainIncludes"] = test_single_input_fail
            self.sv.validate_domainIncludes_field(record)
        with self.assertRaises(SchemaValidationError):
            record["http://schema.org/domainIncludes"] = test_list_input_fail
            self.sv.validate_domainIncludes_field(record)
        try:
            record["http://schema.org/domainIncludes"] = test_single_input_success
            self.sv.validate_domainIncludes_field(record)
        except SchemaValidationError:
            self.fail("validate_domainincludes_field raise Exception unexpectly")
        try:
            record["http://schema.org/domainIncludes"] = test_list_input_success
            self.sv.validate_domainIncludes_field(record)
        except SchemaValidationError:
            self.fail("validate_domainincludes_field raise Exception unexpectly")

    def test_validate_rangecludes_field(self):
        """Test validate_rangeincludes_field function"""
        test_single_input_fail = {"@id": "http://schema.biothings.io/Kk"}
        test_list_input_fail = [
            {"@id": "http://schema.biothings.io/Case"},
            {"@id": "http://schema.biothings.io/Kk"},
        ]
        test_single_input_success = {"@id": "http://schema.biothings.io/Case"}
        test_list_input_success = [
            {"@id": "http://schema.biothings.io/Case"},
            {"@id": "http://schema.biothings.io/Drug"},
        ]

        # test single or multiple rangeIncludes values
        # rangeIncludes issues are always warnings, won't be raised as exceptions
        record = {"@id": "testClass"}
        self.sv.validation_errors = []  # reset validation error list
        record["http://schema.org/rangeIncludes"] = test_single_input_fail
        self.sv.validate_rangeIncludes_field(record)
        self.assertTrue(self.sv.validation_errors)
        err = self.sv.validation_errors[0]
        self.assertTrue(err.warning)
        self.assertEqual(err.error_type, "undefined_rangeincludes")

        record["http://schema.org/rangeIncludes"] = test_list_input_fail
        self.sv.validation_errors = []
        self.sv.validate_rangeIncludes_field(record)
        self.assertTrue(self.sv.validation_errors)
        err = self.sv.validation_errors[0]
        self.assertTrue(err.warning)
        self.assertEqual(err.error_type, "undefined_rangeincludes")

        record["http://schema.org/rangeIncludes"] = test_single_input_success
        self.sv.validation_errors = []
        try:
            self.sv.validate_rangeIncludes_field(record)
        except Exception as err:
            self.fail(f"validate_rangeincludes_field raises Exception unexpectly: {err}")
        self.assertEqual(self.sv.validation_errors, [])

        record["http://schema.org/rangeIncludes"] = test_list_input_success
        self.sv.validation_errors = []
        try:
            self.sv.validate_rangeIncludes_field(record)
        except Exception as err:
            self.fail(f"validate_rangeincludes_field raises Exception unexpectly: {err}")
        self.assertEqual(self.sv.validation_errors, [])

        self.sv.validation_errors = []  # reset validation error list

    def test_check_whether_atid_and_label_match(self):
        """Test check_whether_atid_and_label_match function"""
        test_case_fail = {"@id": "bts:Gene", "rdfs:label": "Variant"}
        test_case_success = {"@id": "bts:Gene", "rdfs:label": "Gene"}
        with self.assertRaises(SchemaValidationError):
            self.sv.check_whether_atid_and_label_match(test_case_fail)
        try:
            self.sv.check_whether_atid_and_label_match(test_case_success)
        except SchemaValidationError:
            self.fail("check_whether_atid_and_label_match raise Exception unexpectly")

    def test_check_duplicate_labels(self):
        """Test check_duplicate_labels function"""
        with self.assertRaises(SchemaValidationError) as cm:
            self.sv_duplicate.check_duplicate_labels()
            self.assertEqual(cm.exception.error_type, "dup_label")
            self.assertTrue(cm.exception.message.find("PhenotypicFeature") != -1)
        try:
            self.sv.check_duplicate_labels()
        except SchemaValidationError:
            self.fail("check_duplicate_labels raises Exception unexpectly")

    def test_validate_property_schema(self):
        """Test validate_property_schema function"""
        property_missing_domain = os.path.join(
            _CURRENT, "data", "property_schema_missing_domain.json"
        )
        property_missing_domain_json = load_json_or_yaml(property_missing_domain)
        with self.assertRaises(SchemaValidationError):
            self.sv.validate_property_schema(property_missing_domain_json)
        property_missing_range = os.path.join(
            _CURRENT, "data", "property_schema_missing_range.json"
        )
        property_missing_range_json = load_json_or_yaml(property_missing_range)
        with self.assertRaises(SchemaValidationError):
            self.sv.validate_property_schema(property_missing_range_json)

    def test_schema_should_correctly_merge_validation_property_on_nested_classes(self):
        """Testing merge_recursive_parents function implicitly"""
        nested_schema_path = os.path.join(_CURRENT, "data", "nested_schema.json")
        nested_schema = load_json_or_yaml(nested_schema_path)

        # test that data is correctly inserted beforehand
        self.assertEqual(len(nested_schema["@graph"][0]["$validation"]["properties"]), 15)
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["description"],
            "The name of the Cvisb Dataset",
        )
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["type"], "string"
        )

        self.assertEqual(len(nested_schema["@graph"][2]["$validation"]["properties"]), 1)
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["description"],
            "Test description",
        )
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["type"], "number"
        )

        self.assertEqual(len(nested_schema["@graph"][3]["$validation"]["properties"]), 1)
        self.assertEqual(
            nested_schema["@graph"][3]["$validation"]["properties"]["name"]["type"], "boolean"
        )

        schema_nx = Schema(nested_schema, validator_options={"validation_merge": True}) #Schema(nested_schema)
        del schema_nx

        # make sure schema is correctly merged after

        # Root class should stay the same
        self.assertEqual(len(nested_schema["@graph"][0]["$validation"]["properties"]), 15)
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["description"],
            "The name of the Cvisb Dataset",
        )
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["type"], "string"
        )

        # the rest of the properties should be inherited from the root class
        self.assertEqual(len(nested_schema["@graph"][2]["$validation"]["properties"]), 15)
        # description and type should override parent class
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["description"],
            "Test description",
        )
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["type"], "number"
        )

        # the rest of the properties should be inherited from the root class
        self.assertEqual(len(nested_schema["@graph"][3]["$validation"]["properties"]), 15)
        # description should be inherited from the parent class
        self.assertEqual(
            nested_schema["@graph"][3]["$validation"]["properties"]["name"]["description"],
            "Test description",
        )
        self.assertEqual(
            nested_schema["@graph"][3]["$validation"]["properties"]["name"]["type"], "boolean"
        )

    def test_schema_should_not_merge_validation_property_on_nested_classes_if_flag_set_to_false(
        self,
    ):
        """Testing merge_recursive_parents function implicitly with merging set to false"""
        nested_schema_path = os.path.join(_CURRENT, "data", "nested_schema.json")
        nested_schema = load_json_or_yaml(nested_schema_path)

        # test that data is correctly inserted beforehand
        self.assertEqual(len(nested_schema["@graph"][0]["$validation"]["properties"]), 15)
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["description"],
            "The name of the Cvisb Dataset",
        )
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["type"], "string"
        )

        self.assertEqual(len(nested_schema["@graph"][2]["$validation"]["properties"]), 1)
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["description"],
            "Test description",
        )
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["type"], "number"
        )

        self.assertEqual(len(nested_schema["@graph"][3]["$validation"]["properties"]), 1)
        self.assertEqual(
            nested_schema["@graph"][3]["$validation"]["properties"]["name"]["type"], "boolean"
        )

        schema_nx = Schema(nested_schema, validator_options={"validation_merge": False})
        del schema_nx

        # data should remain the same after schema creation
        self.assertEqual(len(nested_schema["@graph"][0]["$validation"]["properties"]), 15)
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["description"],
            "The name of the Cvisb Dataset",
        )
        self.assertEqual(
            nested_schema["@graph"][0]["$validation"]["properties"]["name"]["type"], "string"
        )

        self.assertEqual(len(nested_schema["@graph"][2]["$validation"]["properties"]), 1)
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["description"],
            "Test description",
        )
        self.assertEqual(
            nested_schema["@graph"][2]["$validation"]["properties"]["name"]["type"], "number"
        )

        self.assertEqual(len(nested_schema["@graph"][3]["$validation"]["properties"]), 1)
        self.assertEqual(
            nested_schema["@graph"][3]["$validation"]["properties"]["name"]["type"], "boolean"
        )

    def test_extended_schema_validator_works_as_expected(self):
        schema_extended_url = "https://raw.githubusercontent.com/BioSchemas/specifications/master/Gene/jsonld/Gene_v1.0-RELEASE.json"
        schema = Schema(schema_extended_url)
        del schema

    def test_merge_recursive_parents(self):
        """Test recursive merging of parent validations"""
        graph = self._get_graph(self.mock_sv)
        self.assertIsNotNone(graph)

        class_a_index = self._find_idx(self.mock_sv, graph, "http://example.org/Class_A")
        class_a = graph[class_a_index]

        self.mock_sv.merge_recursive_parents(class_a, class_a_index)

        merged_required = graph[class_a_index]["$validation"]["required"]
        self.assertIn("f1", merged_required)
        self.assertIn("f2", merged_required)
        self.assertIn("f3", merged_required)

    def test_merge_all_parent_validations(self):
        """Test merging of parent validations"""
        graph = self._get_graph(self.mock_sv)
        self.assertIsNotNone(graph)

        class_a_index = self._find_idx(self.mock_sv, graph, "http://example.org/Class_A")
        class_a = graph[class_a_index]

        class_a1_index = self._find_idx(self.mock_sv, graph, "http://example.org/Class_A1")
        class_a1 = graph[class_a1_index]

        self.mock_sv.merge_parent_validations(class_a, class_a_index, class_a1)

        merged_required = graph[class_a_index]["$validation"]["required"]
        self.assertIn("f1", merged_required)
        self.assertIn("f3", merged_required)

    def _get_graph(self, sv):
        return sv.extension_schema.get("schema", {}).get("@graph") or sv.extension_schema.get("@graph")

    def _find_idx(self, sv, graph, curie):
        target = sv._norm_id(curie)
        for idx, node in enumerate(graph):
            if sv._norm_id(node.get("@id")) == target:
                return idx
        self.fail(f"Could not find {curie} in graph ids: {[n.get('@id') for n in graph]}")


if __name__ == "__main__":
    unittest.main()
