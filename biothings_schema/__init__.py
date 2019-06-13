import os
import json

import networkx as nx
from jsonschema import validate
from jsonschema import validators
# import tabletext

from .base import *
from .utils import *
from .dataload import *
from .curies import *


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
                                if extract_name_from_uri_or_curie(record["@id"]) in parent_classes:
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
    def __init__(self, schema=None):
        if not schema:
            self.load_default_schema()
            print('Preloaded with SchemaOrg Schema.')
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
        self.schema_nx = load_schema_class_into_networkx(self.schemaorg_schema,
                                                   self.schema_extension_only)
        self.schema_nx_extension_only = load_schema_class_into_networkx(self.schema_extension_only)
        self.schema_property_nx = load_schema_property_into_networkx(self.schemaorg_schema, self.schema_extension_only)
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_full_schema()
        # merge together the given schema and the schema defined by schemaorg
        self.schema = merge_schema(self.schema_extension_only,
                                   self.schemaorg_schema)

    def load_default_schema(self):
        """Load default schema, either schema.org or biothings"""
        self.schema = load_schemaorg()
        self.schema_nx = load_schema_class_into_networkx(self.schema)
        self.schema_nx_extension_only = load_schema_class_into_networkx(self.schema)
        self.schema_property_nx = load_schema_property_into_networkx(self.schema)

    def full_schema_graph(self, size=None):
        """Visualize the full schema loaded using graphviz"""
        edges = self.schema_nx_extension_only.edges()
        return visualize(edges, size=size)

    def sub_schema_graph(self, source, include_parents=True, include_children=True, size=None):
        """Visualize a sub-graph of the schema based on a specific node

        """
        scls = SchemaClass(source, self)
        paths = scls.parent_classes
        parents = []
        for _path in paths:
            elements = []
            for _ele in _path:
                elements.append(_ele.name)
            parents.append(elements)
        # handle cases where user want to get all children
        if include_parents is False and include_children:
            edges = list(nx.edge_bfs(self.schema_nx, [source]))
        # handle cases where user want to get all parents
        elif include_parents and include_children is False:
            edges = []
            for _path in parents:
                _path.append(source)
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
        # handle cases where user want to get both parents and children
        elif include_parents and include_children:
            edges = list(nx.edge_bfs(self.schema_nx, [source]))
            for _path in parents:
                _path.append(source)
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
        else:
            raise ValueError("At least one of include_parents and include_children parameter need to be set to True")
        return visualize(edges, size=size)

    def list_all_classes(self):
        """Find all classes defined in the schema"""
        classes = list(self.schema_nx_extension_only.nodes())
        classes = [SchemaClass(_cls, self) for _cls in classes]
        return classes

    def list_all_properties(self):
        """Find all properties defined in the schema"""
        properties = list(self.schema_property_nx.nodes())
        properties = [SchemaProperty(_prop, self) for _prop in properties]
        return properties

    def get_class(self, class_name):
        """Return a SchemaClass instance of the class"""
        return SchemaClass(class_name, self)

    def get_property(self, property_name):
        """Return a SchemaProperty instance of the property"""
        return SchemaProperty(property_name, self)

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
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_class_schema(class_info)
        self.schema["@graph"].append(class_info)
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_full_schema()
        print("Updated the class {} successfully!".format(class_info["rdfs:label"]))
        self.schema_nx = load_schema_class_into_networkx(self.schema)         # pylint: disable=attribute-defined-outside-init

    def update_property(self, property_info):
        """Add a new property into schema
        """
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_property_schema(property_info)
        self.schema["@graph"].append(property_info)
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_schema(self.schema)
        print("Updated the property {} successfully!".format(property_info["rdfs:label"]))

    def export_schema(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.schema, f, sort_keys=True, indent=4,
                      ensure_ascii=False)


class SchemaClass():
    """Class representing an individual class in Schema
    """
    def __init__(self, class_name, schema):
        self.name = class_name
        self.se = schema
        self.CLASS_REMOVE = ["Number", "Integer", "Float", "Text",
                        "CssSelectorType", "URL", "XPathType", "Class",
                        "DataType"]
        self.ALL_CLASSES = self.CLASS_REMOVE + list(self.se.schema_nx_extension_only.nodes())
        # if class is not defined in schema, raise ValueError
        if self.name not in self.ALL_CLASSES:
            # raise ValueError('Class {} is not defined in Schema. Could not access it'.format(self.name))
            print('Class {} is not defined in Schema. Could not access it'.format(self.name))

    def __repr__(self):
        return '<SchemaClass "' + self.name + '">'

    def __str__(self):
        return str(self.name)

    @property
    def description(self):
        if self.name not in self.CLASS_REMOVE:
            # classes might not have descriptions
            if 'description' in self.se.schema_nx.node[self.name]:
                return self.se.schema_nx.node[self.name]['description']
            else:
                return None
        else:
            return None

    @property
    def ancestor_classes(self):
        return list(nx.ancestors(self.se.schema_nx, self.name))

    @property
    def parent_classes(self):
        """Find all parents of a specific class"""
        root_node = list(nx.topological_sort(self.se.schema_nx))
        # When a schema is not a tree with only one root node
        # Set "Thing" as the root node by default
        if 'Thing' in root_node:
            root_node = 'Thing'
        else:
            root_node = root_node[0]
        paths = nx.all_simple_paths(self.se.schema_nx,
                                    source=root_node,
                                    target=self.name)
        paths =  [_path[:-1] for _path in paths]
        parents = []
        for _path in paths:
            elements = []
            for _ele in _path:
                elements.append(SchemaClass(_ele, self.se))
            parents.append(elements)
        return parents

    def list_properties(self, class_specific=True, group_by_class=True):
        """Find properties of a class

        :arg boolean class_specific: specify whether only to return class specific properties or not
        :arg boolean group_by_class: specify whether the output should be grouped by class or not
        """
        def find_class_specific_properties(schema_class):
            """Find properties specifically associated with a given class"""
            if 'uri' not in self.se.schema_nx.node[schema_class]:
                return []
            else:
                schema_uri = self.se.schema_nx.node[schema_class]["uri"]
                properties = []
                for record in self.se.schema["@graph"]:
                    # look for record which is property only
                    if record['@type'] == "rdf:Property":
                        # some property doesn't have domainInclude/rangeInclude parameter
                        if "http://schema.org/domainIncludes" in record:
                            if isinstance(record["http://schema.org/domainIncludes"], dict) and record["http://schema.org/domainIncludes"]["@id"] == schema_uri:
                                properties.append(SchemaProperty(record["rdfs:label"], self.se))
                            elif isinstance(record["http://schema.org/domainIncludes"], list) and [item for item in record["http://schema.org/domainIncludes"] if item["@id"] == schema_uri] != []:
                                properties.append(SchemaProperty(record["rdfs:label"], self.se))
                return properties
        if class_specific:
            properties = [{'class': self.name,
                           'properties': find_class_specific_properties(self.name)}]
        else:
            # find all parent classes
            parents = [[_item.name for _item in _cls] for _cls in self.parent_classes]
            properties = [{'class': self.name,
                           'properties': find_class_specific_properties(self.name)}]
            # update properties, each dict represent properties associated with
            # the class
            for path in parents:
                path.reverse()
                for _parent in path:
                    properties.append({
                        "class": _parent,
                        "properties": find_class_specific_properties(_parent)
                    })
        if group_by_class:
            return properties
        else:
            ungrouped_properties = []
            for _item in properties:
                ungrouped_properties += _item['properties']
            return list(set(ungrouped_properties))

    def used_by(self):
        """Find where a given class is used as a value of a property"""
        usages = []
        schema_uri = self.se.schema_nx.node[self.name]["uri"]
        for record in self.se.schema["@graph"]:
            usage = {}
            if record["@type"] == "rdf:Property":
                if "http://schema.org/rangeIncludes" in record:
                    p_range = dict2list(record["http://schema.org/rangeIncludes"])
                    for _doc in p_range:
                        if _doc['@id'] == schema_uri:
                            usage["property"] = SchemaProperty(record["rdfs:label"], self.se)
                            p_domain = dict2list(record["http://schema.org/domainIncludes"])
                            cls_using_property = [extract_name_from_uri_or_curie(record["@id"], self.se.schema) for record in p_domain]
                            usage["property_used_on_class"] = [SchemaClass(_cls, self.se) for _cls in cls_using_property]
                            usage["description"] = record["rdfs:comment"]
            if usage:
                usages.append(usage)
        return usages

    @property
    def child_classes(self):
        """Find schema classes that directly inherit from the given class
        """
        children = list(self.se.schema_nx.successors(self.name))
        children = [SchemaClass(_child, self.se) for _child in children]
        return children

    @property
    def descendant_classes(self):
        """Find schema classes that inherit from the given class
        """
        descendants = list(nx.descendants(self.se.schema_nx,
                                          self.name))
        descendants = [SchemaClass(_des, self.se) for _des in descendants]
        return descendants

    def describe(self):
        """Find details about a specific schema class
        """
        class_info = {'properties': self.list_properties(class_specific=False),
                      'description': self.description,
                      'uri': self.se.schema_nx.node[self.name]["uri"],
                      'usage': self.used_by(),
                      'child_classes': self.child_classes,
                      'parent_classes': self.parent_classes}
        return class_info


class SchemaProperty():
    """Class representing an individual property in Schema
    """

    def __init__(self, property_name, schema):
        self.name = property_name
        self.se = schema
        # if property is not defined in schema, raise ValueError
        if self.name not in self.se.schema_property_nx.nodes():
            #raise ValueError('Property {} is not defined in Schema. Could not access it'.format(self.name))
            print('Property {} is not defined in Schema. Could not access it'.format(self.name))

    def __repr__(self):
        return '<SchemaProperty "' + self.name + '"">'

    def __str__(self):
        return str(self.name)

    @property
    def description(self):
        # some properties doesn't have descriptions
        if 'description' in self.se.schema_property_nx.node[self.name]:
            return self.se.schema_property_nx.node[self.name]['description']
        else:
            return None

    @property
    def parent_properties(self):
        """Find all parents of a specific class"""
        parents = list(nx.ancestors(self.se.schema_property_nx,
                                    self.name))
        parents = [SchemaProperty(_parent, self.se) for _parent in parents]
        return parents

    @property
    def child_properties(self):
        """Find schema properties that directly inherit from the given property
        """
        children =  list(self.se.schema_property_nx.successors(self.name))
        children = [SchemaProperty(_child, self.se) for _child in children]
        return children

    @property
    def descendant_properties(self):
        """Find schema properties that inherit from the given property
        """
        descendants = list(nx.descendants(self.se.schema_property_nx,
                                          self.name))
        descendants = [SchemaProperty(_descendant, self.se) for _descendant in descendants]
        return descendants

    def describe(self):
        """Find details about a specific property
        """
        property_info = {'child_properties': self.child_properties,
                         'descendant_properties': self.descendant_properties,
                         'parent_properties': self.parent_properties,
                         'domain': [],
                         'range': []}
        for record in self.se.schema["@graph"]:
            if record["@type"] == "rdf:Property":
                if record["rdfs:label"] == self.name:
                    property_info["id"] = record["rdfs:label"]
                    property_info["description"] = record["rdfs:comment"]
                    #property_info["uri"] = self.curie2uri(record["@id"])
                    if "http://schema.org/domainIncludes" in record:
                        p_domain = dict2list(record["http://schema.org/domainIncludes"])
                        property_info["domain"] = [SchemaClass(extract_name_from_uri_or_curie(record["@id"], self.se.schema), self.se) for record in p_domain]
                    if "http://schema.org/rangeIncludes" in record:
                        p_range = dict2list(record["http://schema.org/rangeIncludes"])
                        property_info["range"] = [SchemaClass(extract_name_from_uri_or_curie(record["@id"], self.se.schema), self.se) for record in p_range]
        return property_info
