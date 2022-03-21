import os.path
# import warnings

import jsonschema
import networkx as nx

from .settings import (
    VALIDATION_FIELD,
    # ALT_VALIDATION_FIELDS,
    # DEFAULT_JSONSCHEMA_METASCHEMA
)
from .utils import (
    dict2list,
    str2list,
    find_duplicates
)
from .dataload import (
    load_json_or_yaml,
    load_base_schema
)
from .curies import (
    preprocess_schema,
    extract_name_from_uri_or_curie
)


_ROOT = os.path.abspath(os.path.dirname(__file__))


class SchemaValidationError(ValueError):
    def __init__(self, message="", error_type=None, field=None, record_id=None, long_message=None, warning=False):
        self.message = message
        self.error_type = error_type            # the optional error_type
        self.field = field                      # the specific field name with the error, if applicable
        self.record_id = record_id              # @id field of a class or property record with the error, if applicable
        self.long_message = long_message        # optional longer description of the error message
        self.warning = warning                  # True if it's a warning, the exception will not be raised, only recorded.
        super(SchemaValidationError, self).__init__(message)

    def __repr__(self):
        _msg = f'"{self.message}"'
        for attr in ['error_type', 'field', 'record_id']:
            if getattr(self, attr, None):
                _msg += f', {attr}="{getattr(self, attr)}"'
        return f"<{self.__class__.__name__}({_msg})>"

class SchemaValidationWarning(SchemaValidationError):
    pass

class SchemaValidator():
    """Validate Schema against SchemaOrg standard

    Validation Criterias:
    1. Data Structure wise:
      > "@id", "@context", "@graph"
      > Each element in "@graph" should contain "@id", "@type", "rdfs:comment",
      "rdfs:label"
      > validate against JSON Schema
      > Should validate the whole structure, and also validate property and
      value separately
    2. Data Content wise:
      > "@id" field should match with "rdfs:label" field
      > all prefixes used in the file should be defined in "@context"
      > There should be no duplicate "@id"
      > Class specific
        > rdfs:label field should be capitalize the first character of each
          word
        > the value of "rdfs:subClassOf" should be present in the schema or in
          the core vocabulary
      > Property specific
        > rdfs:label field should be carmelCase
        > the value of "schema:domainIncludes" should be present in the schema
          or in the core vocabulary
        > the value of "schema:rangeIncludes" should be present in the schema
          or in the core vocabulary
      # TODO: Check if value of inverseof field is defined in the schema
      # TODO: Check inverseof from both properties
    """
    def __init__(self, schema, schema_nx, base_schema=None, validation_merge=True, raise_on_validation_error=True):
        self.validation_merge = validation_merge
        if base_schema is None or isinstance(base_schema, (list, tuple)):
            base_schema = load_base_schema(base_schema=base_schema)

        self.base_schema = self._process_schema(base_schema)
        self.extension_schema = self._process_schema(schema)
        self.all_classes = self.base_schema['classes'] + self.extension_schema['classes']
        self.all_schemas = self.base_schema['schema']['@graph'] + self.extension_schema["schema"]["@graph"]
        self.schema_nx = schema_nx

        self.validation_errors = []        # store all validation errors
        self.raise_on_validation_error = raise_on_validation_error      # If True, raise except at the first error

    @staticmethod
    def _process_schema(schema):
        _schema = {
            'schema': preprocess_schema(schema),
            'classes': [],
            'properties': []
        }
        for _record in _schema['schema']['@graph']:
            if "@type" in _record:
                _type = str2list(_record["@type"])
                if "rdfs:Property" in _type:
                    _schema['properties'].append(_record["@id"])
                elif "rdfs:Class" in _type:
                    _schema['classes'].append(_record["@id"])
        return _schema

    def report_validation_error(self, err_msg, **kwargs):
        '''Report valiation error, either keep it in self.validation_errors or raise an exception.
           if warning is True, do not raise an exception regardless self.raise_on_validation_error
        '''

        err = SchemaValidationWarning(err_msg, **kwargs) if kwargs.get('warning', False) else SchemaValidationError(err_msg, **kwargs)
        if not err.warning and self.raise_on_validation_error:
            raise err
        else:
            self.validation_errors.append(err)

    def validate_class_label(self, label_uri):
        """ Check if the first character of class label is capitalized
        """
        label = extract_name_from_uri_or_curie(label_uri)
        if not label[0].isupper():
            # raise ValueError('Class label {} is incorrect. The first letter of each word should be capitalized!'.format(label))
            self.report_validation_error(
                f'Class label {label} is incorrect. The first letter of each word should be capitalized.',
                error_type="invalid_class_label", record_id=label_uri
            )

    def validate_property_label(self, label_uri):
        """ Check if the first character of property label is lower case
        """
        label = extract_name_from_uri_or_curie(label_uri)
        if not label[0].islower():
            # raise ValueError('Property label {} is incorrect. The first letter of the first word should be lower case!'.format(label))
            self.report_validation_error(
                f'Property label {label} is incorrect. The first letter of the first word should be lower case.',
                error_type="invalid_property_label", record_id=label_uri
            )

    def validate_subclassof_field(self, subclassof_value):
        """ Check if the value of "subclassof" is included in the schema file
        """
        subclassof_value = dict2list(subclassof_value)
        for record in subclassof_value:
            if record["@id"] not in self.all_classes:
                # raise KeyError('Value of subclassof : {} is not defined in the schema.'.format(record["@id"]))
                self.report_validation_error('Value of subclassof : {} is not defined in the schema.'.format(record["@id"]))

    def validate_domainIncludes_field(self, record):
        """ Check if the value of "domainincludes" is a defined class"""
        domainincludes_value = record.get("http://schema.org/domainIncludes", {})
        if domainincludes_value:
            domainincludes_value = dict2list(domainincludes_value)
            for cls in domainincludes_value:
                if cls["@id"] not in self.all_classes:
                    # raise KeyError('Value of domainincludes: {} is not defined in the schema.'.format(cls["@id"]))
                    self.report_validation_error(
                        f"Value of domainincludes: \"{cls['@id']}\" is not defined in the schema.",
                        error_type="undefined_domainincludes_class", record_id=record['@id']
                    )
        else:
            # raise a warning
            self.report_validation_error('Missing "domainIncludes"', error_type="missing_domainincludes", record_id=record["@id"], warning=True)

    def validate_rangeIncludes_field(self, record):
        """ Check if the value of "rangeincludes" is defined"""
        rangeincludes_value = record.get("http://schema.org/rangeIncludes", {})
        if rangeincludes_value:
            rangeincludes_value = dict2list(rangeincludes_value)
            for cls in rangeincludes_value:
                if cls["@id"] not in self.all_classes:
                    # raise KeyError('Value of rangeincludes: {} is not defined in the schema.'.format(cls["@id"]))
                    self.report_validation_error(
                        f"Value of rangeincludes: \"{cls['@id']}\" is not defined in the schema.",
                        error_type="undefined_rangeincludes", record_id=record['@id'], warning=True)
        else:
            # raise a warning
            self.report_validation_error('Missing "rangeIncludes"', error_type="missing_rangeincludes", record_id=record["@id"], warning=True)

    def check_whether_atid_and_label_match(self, record):
        """ Check if @id field matches with the "rdfs:label" field
        """
        _id = extract_name_from_uri_or_curie(record["@id"])
        if _id != record["rdfs:label"]:
            # raise ValueError("id and label not match: {}".format(record))
            self.report_validation_error(f'id and label not match: {record["rdfs:label"]}', error_type="unmatched_label", record_id=_id)

    def check_duplicate_labels(self):
        """Check for duplication labels in the schema"""
        labels = [_record['rdfs:label'] for _record in self.extension_schema["schema"]["@graph"]]
        duplicates = find_duplicates(labels)
        if duplicates:
            # raise ValueError('Duplicates detected in graph: {}'.format(duplicates))
            self.report_validation_error(f'Duplicates labels detected in @graph: {duplicates}', error_type="dup_label")

    def validate_schema(self, schema):
        """Validate schema against SchemaORG-style JSON-LD
        """
        json_schema_path = os.path.join(_ROOT, 'data', 'schema.json')
        json_schema = load_json_or_yaml(json_schema_path)
        try:
            jsonschema.validate(schema, json_schema)
        except jsonschema.ValidationError as err:
            self.report_validation_error(repr(err), long_message=str(err))

    def validate_property_schema(self, record):
        """Validate schema against SchemaORG property definition standard
        """
        json_schema_path = os.path.join(_ROOT,
                                        'data',
                                        'property_json_schema.json')
        json_schema = load_json_or_yaml(json_schema_path)
        try:
            jsonschema.validate(record, json_schema)
        except jsonschema.ValidationError as err:
            self.report_validation_error(repr(err), error_type="invalid_property", record_id=record["@id"], long_message=str(err))

    def validate_class_schema(self, record):
        """Validate schema against SchemaORG class definition standard
        """
        json_schema_path = os.path.join(_ROOT,
                                        'data',
                                        'class_json_schema.json')
        json_schema = load_json_or_yaml(json_schema_path)
        try:
            jsonschema.validate(record, json_schema)
        except jsonschema.ValidationError as err:
            self.report_validation_error(repr(err), error_type="invalid_class", record_id=record["@id"], long_message=str(err))

    def validate_json_schema(self, json_schema):
        """Make sure the json schema provided in the VALIDATION_FIELD field is valid

        source code from: https://python-jsonschema.readthedocs.io/en/stable/_modules/jsonschema/validators/#validate
        TODO: Maybe add additional check,e.g. fields in "required" should appear in "properties"
        """
        cls = jsonschema.validators.validator_for(json_schema)
        try:
            cls.check_schema(json_schema)
        except jsonschema.SchemaError as err:
            self.report_validation_error(repr(err), error_type="invalid_validation_schema", long_message=str(err))

    def validate_validation_field(self, record):
        """Validate the VALIDATION_FIELD
        Validation creteria:
            * must include a "properties" field
            * must be a valid jsonschema schema
            * all properties specified must be defined in its class or parent classes
          TODO: 4. POTENTIALLY, VALUE OF $VALIDATION IS A URL
        """
        _id = record["@id"]
        if VALIDATION_FIELD in record:
            if 'properties' not in record[VALIDATION_FIELD]:
                # raise KeyError(f'properties not in {VALIDATION_FIELD} field')
                self.report_validation_error(
                    f'"properties" not found in {VALIDATION_FIELD} field',
                    error_type="invalid_validation_schema", record_id=_id
                )
            else:
                # validate the json schema
                self.validate_json_schema(record[VALIDATION_FIELD])
                properties = record[VALIDATION_FIELD]["properties"].keys()
                # find all parents of the class
                paths = nx.all_simple_paths(self.schema_nx,
                                            source='http://schema.org/Thing',
                                            target=_id)
                parent_classes = set()
                for _path in paths:
                    for _item in _path:
                        parent_classes.add(_item)
                if not parent_classes:
                    # raise ValueError(f'Class "{_id}" has no path to the root "schema:Thing" class')
                    self.report_validation_error(
                        f'Class "{_id}" has no path to the root "schema:Thing" class',
                        error_type="no_path_to_root", record_id=_id
                    )
                # loop through all properties and check if the value of
                # domainIncludes belong to one of the parent_classes
                for _property in properties:
                    matched = False
                    for _record in self.all_schemas:
                        if _record["rdfs:label"] == _property:
                            domainincludes_value = dict2list(_record["http://schema.org/domainIncludes"])
                            for cls in domainincludes_value:
                                if cls["@id"] in parent_classes:
                                    matched = True
                    if not matched:
                        # raise ValueError(f'field "{_property}" in "{VALIDATION_FIELD}" is not defined in this class or any of its parent classes')
                        self.report_validation_error(
                            f'field "{_property}" in "{VALIDATION_FIELD}" is not defined in this class or any of its parent classes',
                            error_type="invalid_validation_schema", field=_property, record_id=_id
                        )
        else:
            pass

    def merge(self, source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self.merge(value, node)
            else:
                if key not in destination:
                    destination[key] = value

        return destination

    def merge_parent_validations(self, schema, schema_index, parent):
        if parent and parent.get(VALIDATION_FIELD):
            self.extension_schema['schema']['@graph'][schema_index][VALIDATION_FIELD] = \
                self.merge(parent[VALIDATION_FIELD], self.extension_schema['schema']['@graph'][schema_index][VALIDATION_FIELD])

    def merge_recursive_parents(self, record, schema_index):
        parent_schema = None
        parent_index = None
        if record.get('rdfs:subClassOf'):
            parent_index = next((
                parent_index for parent_index, schema in enumerate(self.extension_schema['schema']['@graph'])
                if schema['@id'] == record.get('rdfs:subClassOf').get('@id')
            ), None)
            if parent_index is not None:
                parent_schema = self.extension_schema['schema']['@graph'][parent_index]
        self.merge_parent_validations(record, schema_index, parent_schema)
        if parent_schema and parent_index and parent_schema.get('rdfs:subClassOf'):
            self.merge_recursive_parents(parent_schema, parent_index)

    def validate_full_schema(self):
        """ Main function to validate schema
        """
        self.check_duplicate_labels()
        for count, record in enumerate(self.extension_schema['schema']['@graph']):
            self.check_whether_atid_and_label_match(record)
            if record['@type'] == "rdfs:Class":
                # parent_schema = None
                # if record.get('rdfs:subClassOf'):
                #     parent_schema = next((schema for schema in self.extension_schema['schema']['@graph']
                #                           if schema['@id'] == record.get('rdfs:subClassOf').get('@id')), None)
                if self.validation_merge:
                    self.merge_recursive_parents(record, count)

                #self.merge_parent_validations(record, count, parent_schema)
                self.validate_class_schema(record)
                self.validate_class_label(record["@id"])
                self.validate_validation_field(record)
            elif record['@type'] == "rdf:Property":
                self.validate_property_schema(record)
                self.validate_property_label(record["@id"])
                self.validate_domainIncludes_field(record)
                self.validate_rangeIncludes_field(record)
            else:
                self.report_validation_error(
                    f"@type value (\"{record['@type']}\") is neither \"rdfs:Class\" nor \"rdf:Property\": \"{record['@id']}\"",
                    error_type="non_class_or_property_@type", record_id=record["@id"], warning=True
                )
