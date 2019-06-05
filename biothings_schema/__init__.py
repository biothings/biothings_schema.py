import os
import json

import networkx as nx
from jsonschema import validate
from jsonschema import validators
# import tabletext

from .base import *
from .utils import *


_ROOT = os.path.abspath(os.path.dirname(__file__))


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
    def __init__(self, schema, schema_nx):
        self.schemaorg = {'schema': load_schemaorg(),
                          'classes': [],
                          'properties': []}
        for _record in self.schemaorg['schema']['@graph']:
            if "@type" in _record:
                _type = str2list(_record["@type"])
                if "rdfs:Property" in _type:
                    self.schemaorg['properties'].append(_record["@id"])
                elif "rdfs:Class" in _type:
                    self.schemaorg['classes'].append(_record["@id"])
        self.extension_schema = {'schema': expand_curies_in_schema(schema),
                                 'classes': [],
                                 'properties': []}
        for _record in self.extension_schema['schema']["@graph"]:
            _type = str2list(_record["@type"])
            if "rdfs:Property" in _type:
                self.extension_schema['properties'].append(_record["@id"])
            elif "rdfs:Class" in _type:
                self.extension_schema['classes'].append(_record["@id"])
        self.all_classes = self.schemaorg['classes'] + self.extension_schema['classes']
        self.all_schemas = self.schemaorg['schema']['@graph'] + self.extension_schema["schema"]["@graph"]
        self.schema_nx = schema_nx

    def validate_class_label(self, label_uri):
        """ Check if the first character of class label is capitalized
        """
        label = extract_name_from_uri_or_curie(label_uri)
        if not label[0].isupper():
            raise ValueError('Class label {} is incorrect. The first letter of each word should be capitalized!'.format(label))

    def validate_property_label(self, label_uri):
        """ Check if the first character of property label is lower case
        """
        label = extract_name_from_uri_or_curie(label_uri)
        if not label[0].islower():
            raise ValueError('Property label {} is incorrect. The first letter of the first word should be lower case!'.format(label))

    def validate_subclassof_field(self, subclassof_value):
        """ Check if the value of "subclassof" is included in the schema file
        """
        subclassof_value = dict2list(subclassof_value)
        for record in subclassof_value:
            if record["@id"] not in self.all_classes:
                raise KeyError('Value of subclassof : {} is not defined in the schema.'.format(record["@id"]))

    def validate_domainIncludes_field(self, domainincludes_value):
        """ Check if the value of "domainincludes" is included in the schema
        file
        """
        domainincludes_value = dict2list(domainincludes_value)
        for record in domainincludes_value:
            if record["@id"] not in self.all_classes:
                raise KeyError('Value of domainincludes: {} is not defined in the schema.'.format(record["@id"]))

    def validate_rangeIncludes_field(self, rangeincludes_value):
        """ Check if the value of "rangeincludes" is included in the schema
        file
        """
        rangeincludes_value = dict2list(rangeincludes_value)
        for record in rangeincludes_value:
            if record["@id"] not in self.all_classes:
                raise KeyError('Value of rangeincludes: {} is not defined in the schema.'.format(record["@id"]))

    def check_whether_atid_and_label_match(self, record):
        """ Check if @id field matches with the "rdfs:label" field
        """
        _id = extract_name_from_uri_or_curie(record["@id"])
        if _id != record["rdfs:label"]:
            raise ValueError("id and label not match: {}".format(record))

    def check_duplicate_labels(self):
        """ Check for duplication in the schema
        """
        labels = [_record['rdfs:label'] for _record in self.extension_schema["schema"]["@graph"]]
        duplicates = find_duplicates(labels)
        if duplicates:
            raise ValueError('Duplicates detected in graph: {}'.format(duplicates))

    def validate_schema(self, schema):
        """Validate schema against SchemaORG standard
        """
        json_schema_path = os.path.join(_ROOT, 'data', 'schema.json')
        json_schema = load_json_or_yaml(json_schema_path)
        return validate(schema, json_schema)

    def validate_property_schema(self, schema):
        """Validate schema against SchemaORG property definition standard
        """
        json_schema_path = os.path.join(_ROOT,
                                        'data',
                                        'property_json_schema.json')
        json_schema = load_json_or_yaml(json_schema_path)
        return validate(schema, json_schema)

    def validate_class_schema(self, schema):
        """Validate schema against SchemaORG class definition standard
        """
        json_schema_path = os.path.join(_ROOT,
                                        'data',
                                        'class_json_schema.json')
        json_schema = load_json_or_yaml(json_schema_path)
        return validate(schema, json_schema)

    def validate_json_schema(self, json_schema):
        """Make sure the json schema provided in the $validation field is valid

        source code from: https://python-jsonschema.readthedocs.io/en/stable/_modules/jsonschema/validators/#validate
        TODO: Maybe add additional check,e.g. fields in "required" should appear in "properties"
        """
        cls = validators.validator_for(json_schema)
        cls.check_schema(json_schema)

    def validate_validation_field(self, schema):
        """Validate the $validation field
        Validation creteria:
        Make sure all properties specified are documented in schema
          TODO: 4. POTENTIALLY, VALUE OF $VALIDATION IS A URL
        """
        if "$validation" in schema:
            if 'properties' not in schema["$validation"]:
                raise KeyError('properties not in $validation field')
            else:
                # validate the json schema
                self.validate_json_schema(schema["$validation"])
                properties = schema["$validation"]["properties"].keys()
                # find all parents of the class
                paths = nx.all_simple_paths(self.schema_nx,
                                            source='Thing',
                                            target=schema["rdfs:label"])
                parent_classes = set()
                for _path in paths:
                    for _item in _path:
                        parent_classes.add(_item)
                # loop through all properties and check if the value of
                # domainIncludes belong to one of the parent_classes
                for _property in properties:
                    matched = False
                    for _record in self.all_schemas:
                        if _record["rdfs:label"] == _property:
                            domainincludes_value = dict2list(_record["http://schema.org/domainIncludes"])
                            for record in domainincludes_value:
                                if uri2label(record["@id"]) in parent_classes:
                                    matched = True
                    if not matched:
                        raise ValueError('field {} in $validation is not correctly documented'.format(_property))
        else:
            pass

    def validate_full_schema(self):
        """ Main function to validate schema
        """
        self.check_duplicate_labels()
        for record in self.extension_schema['schema']['@graph']:
            self.check_whether_atid_and_label_match(record)
            if record['@type'] == "rdfs:Class":
                self.validate_class_schema(record)
                self.validate_class_label(record["@id"])
                self.validate_validation_field(record)
            elif record['@type'] == "rdf:Property":
                self.validate_property_schema(record)
                self.validate_property_label(record["@id"])
                self.validate_domainIncludes_field(record["http://schema.org/domainIncludes"])
                self.validate_rangeIncludes_field(record["http://schema.org/rangeIncludes"])
            else:
                raise ValueError('wrong @type value found: {}'.format(record))


class Schema():
    """Class representing schema
    """
    # TODO: change path to schema, JSON/YAML/FILE PATH/HTTP URL
    def __init__(self, schema=None):
        if not schema:
            self.load_default_schema()
            print('Preloaded with BioLink schema.')
        else:
            self.load_schema(schema)

    def extract_validation_info(self, schema=None, return_results=True):
        """Extract the $validation field and organize into self.validation"""
        self.validation = {}
        # if no schema is provided, try self.schema
        if not schema:
            schema = self.schema
        if "@graph" not in schema:
            raise ValueError('No valid schmea provided')
        for _doc in schema['@graph']:
            if "$validation" in _doc:
                self.validation[_doc['@id']] = _doc['$validation']
        if return_results:
            return self.validation

    def load_schema(self, schema):
        """Load schema and convert it to networkx graph"""
        self.schema_extension_only = expand_curies_in_schema(load_json_or_yaml(schema))
        self.extract_validation_info(schema=self.schema_extension_only,
                                     return_results=False)
        self.schemaorg_schema = expand_curies_in_schema(load_schemaorg())
        self.schema_nx = load_schema_into_networkx(self.schemaorg_schema,
                                                   self.schema_extension_only)
        self.schema_nx_extension_only = load_schema_into_networkx(self.schema_extension_only)
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_full_schema()
        # merge together the given schema and the schema defined by schemaorg
        self.schema = merge_schema(self.schema_extension_only,
                                   self.schemaorg_schema)

    def load_default_schema(self):
        """Load default schema, either schema.org or biothings"""
        self.schema = load_default()
        self.schema_nx = load_schema_into_networkx(self.schema)

    def full_schema_graph(self, size=None):
        """Visualize the full schema loaded using graphviz"""
        edges = self.schema_nx_extension_only.edges()
        return visualize(edges, size=size)

    def sub_schema_graph(self, source, direction, size=None):
        """Visualize a sub-graph of the schema based on a specific node
        """
        # handle cases where user want to get all children
        if direction == 'down':
            edges = list(nx.edge_bfs(self.schema_nx, [source]))
            return visualize(edges, size=size)
        # handle cases where user want to get all parents
        elif direction == 'up':
            paths = self.find_parent_classes(source)
            edges = []
            for _path in paths:
                _path.append(source)
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
            return visualize(edges, size=size)
        # handle cases where user want to get both parents and children
        elif direction == "both":
            paths = self.find_parent_classes(source)
            edges = list(nx.edge_bfs(self.schema_nx, [source]))
            for _path in paths:
                _path.append(source)
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
            return visualize(edges, size=size)
        else:
            raise ValueError("The value of direction parameter could only be down, up or both")

    def fetch_all_classes(self):
        """Find all classes defined in the schema"""
        return list(self.schema_nx_extension_only.nodes())

    def find_parent_classes(self, schema_class):
        """Find all parents of a specific class"""
        root_node = list(nx.topological_sort(self.schema_nx))
        # When a schema is not a tree with only one root node
        # Set "Thing" as the root node by default
        if 'Thing' in root_node:
            root_node = 'Thing'
        else:
            root_node = root_node[0]
        paths = nx.all_simple_paths(self.schema_nx,
                                    source=root_node,
                                    target=schema_class)
        return [_path[:-1] for _path in paths]

    def find_class_specific_properties(self, schema_class):
        """Find properties specifically associated with a given class"""
        schema_uri = self.schema_nx.node[schema_class]["uri"]
        properties = []
        for record in self.schema["@graph"]:
            # look for record which is property only
            if record['@type'] == "rdf:Property":
                # some property doesn't have domainInclude/rangeInclude parameter
                if "http://schema.org/domainIncludes" in record:
                    if isinstance(record["http://schema.org/domainIncludes"], dict) and record["http://schema.org/domainIncludes"]["@id"] == schema_uri:
                        properties.append(record["rdfs:label"])
                    elif isinstance(record["http://schema.org/domainIncludes"], list) and [item for item in record["http://schema.org/domainIncludes"] if item["@id"] == schema_uri] != []:
                        properties.append(record["rdfs:label"])
        return properties

    def find_all_class_properties(self, schema_class):
        """Find all properties associated with a given class
        """
        # find all parent classes
        parents = self.find_parent_classes(schema_class)
        properties = [{'class': schema_class,
                       'properties': self.find_class_specific_properties(schema_class)}]
        # update properties, each dict represent properties associated with
        # the class
        for path in parents:
            path.reverse()
            for _parent in path:
                properties.append({
                    "class": _parent,
                    "properties": self.find_class_specific_properties(_parent)
                })
        return properties

    def find_class_usages(self, schema_class):
        """Find where a given class is used as a value of a property"""
        usages = []
        schema_uri = self.schema_nx.node[schema_class]["uri"]
        for record in self.schema["@graph"]:
            usage = {}
            if record["@type"] == "rdf:Property":
                if "http://schema.org/rangeIncludes" in record:
                    p_range = dict2list(record["http://schema.org/rangeIncludes"])
                    for _doc in p_range:
                        if _doc['@id'] == schema_uri:
                            usage["property"] = record["rdfs:label"]
                            p_domain = dict2list(record["http://schema.org/domainIncludes"])
                            usage["property_used_on_class"] = unlist([uri2label(record["@id"], self.schema) for record in p_domain])
                            usage["description"] = record["rdfs:comment"]
            if usage:
                usages.append(usage)
        return usages

    def find_child_classes(self, schema_class):
        """Find schema classes that directly inherit from the given class
        """
        return unlist(list(self.schema_nx.successors(schema_class)))

    def explore_class(self, schema_class):
        """Find details about a specific schema class
        """
        class_info = {'properties': self.find_all_class_properties(schema_class),
                      'description': self.schema_nx.node[schema_class]['description'],
                      'uri': self.schema_nx.node[schema_class]["uri"],
                      'usage': self.find_class_usages(schema_class),
                      'child_classes': self.find_child_classes(schema_class),
                      'parent_classes': self.find_parent_classes(schema_class)}
        return class_info

    def explore_property(self, schema_property):
        """Find details about a specific property
        """
        property_info = {}
        for record in self.schema["@graph"]:
            if record["@type"] == "rdf:Property":
                if record["rdfs:label"] == schema_property:
                    property_info["id"] = record["rdfs:label"]
                    property_info["description"] = record["rdfs:comment"]
                    #property_info["uri"] = self.curie2uri(record["@id"])
                    if "http://schema.org/domainIncludes" in record:
                        p_domain = dict2list(record["http://schema.org/domainIncludes"])
                    property_info["domain"] = unlist([uri2label(record["@id"], self.schema) for record in p_domain])
                    if "http://schema.org/rangeIncludes" in record:
                        p_range = dict2list(record["http://schema.org/rangeIncludes"])
                    property_info["range"] = unlist([uri2label(record["@id"], self.schema) for record in p_range])
        return property_info

    def validate_against_schema(self, json_doc, class_uri):
        """Validate a json document against it's JSON schema defined in Schema

        :arg dict json_doc: The JSON Document to be validated
        :arg str class_uri: The URI of the class which has JSON schema
        """
        if not self.validation:
            raise RuntimeError("The Schema File doesn't contain any validation field")
        elif class_uri not in self.validation:
            raise KeyError("{} not in the the list of URIs [{}] which has JSON-Schema embed".format(class_uri,
                                          list(self.validation.keys())))
        else:
            validate(json_doc, self.validation[class_uri])
            print('The JSON document is valid')

    def generate_class_template(self):
        """Generate a template for schema class
        """
        template = {
            "@id": "uri or curie of the class",
            "@type": "rdfs:Class",
            "rdfs:comment": "description of the class",
            "rdfs:label": "class label, should match @id",
            "rdfs:subClassOf": {
                "@id": "parent class, could be list"
            },
            "schema:isPartOf": {
                "@id": "http://schema.biothings.io"
            }
        }
        return template

    def generate_property_template(self):
        """Generate a template for schema property
        """
        template = {
            "@id": "url or curie of the property",
            "@type": "rdf:Property",
            "rdfs:comment": "description of the property",
            "rdfs:label": "carmel case, should match @id",
            "schema:domainIncludes": {
                "@id": "class which use it as a property, could be list"
            },
            "schema:isPartOf": {
                "@id": "http://schema.biothings.io"
            },
            "schema:rangeIncludes": {
                "@id": "relates a property to a class that constitutes (one of) the expected type(s) for values of the property"
            }
        }
        return template

    def update_class(self, class_info):
        """Add a new class into schema
        """
        validate_class_schema(class_info)
        self.schema["@graph"].append(class_info)
        validate_schema(self.schema)
        print("Updated the class {} successfully!".format(class_info["rdfs:label"]))
        self.schema_nx = load_schema_into_networkx(self.schema)         # pylint: disable=attribute-defined-outside-init

    def update_property(self, property_info):
        """Add a new property into schema
        """
        validate_property_schema(property_info)
        self.schema["@graph"].append(property_info)
        validate_schema(self.schema)
        print("Updated the property {} successfully!".format(property_info["rdfs:label"]))

    def export_schema(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.schema, f, sort_keys=True, indent=4,
                      ensure_ascii=False)
