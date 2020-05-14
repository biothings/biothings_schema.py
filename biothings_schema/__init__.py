import os
import json
import warnings
from functools import partial
import inspect

import networkx as nx
import jsonschema
from jsonschema import validate
from jsonschema import validators
# import tabletext

from .base import *
from .utils import *
from .dataload import *
from .curies import *


_ROOT = os.path.abspath(os.path.dirname(__file__))

METHODS_RETURN_LIST = ['ancestor_classes',
                       'child_classes',
                       'descendant_classes',
                       'parent_classes',
                       'list_properties',
                       'used_by',
                       'domain',
                       'range',
                       'parent_properties',
                       'child_properties',
                       'descendant_properties']

METHODS_RETURN_DICT = ['describe']

METHODS_RETURN_STR = ['description',
                      'label',
                      'prefix',
                      'uri',
                      'inverse_property']


def check_defined(scls, method_name):
    if not scls.defined_in_schema:
        if method_name in METHODS_RETURN_LIST:
            return []
        elif method_name in METHODS_RETURN_STR:
            return ''
        elif method_name in METHODS_RETURN_DICT:
            return {}
    else:
        return scls.defined_in_schema


def transform_schemaclasses_lst(se, scls_list, output_type):
    """Transform a list of schemaclass classes"""
    if output_type == "uri":
        return scls_list
    elif output_type == "curie":
        return list(map(se.cls_converter.get_curie,
                        scls_list))
    elif output_type == "label":
        return list(map(se.cls_converter.get_label,
                        scls_list))
    elif output_type == "PythonClass":
        return list(map(partial(SchemaClass, schema=se),
                        scls_list))
    else:
        raise ValueError('output_type wrong. Should be one of uri, curie, label or PythonClass')


def transform_property_info_list(se, prop_list, output_type):
    """Transform a list of properties"""
    props = [{"description": _prop.get("description"),
              "domain": transform_schemaclasses_lst(se,
                                                    _prop.get("domain"),
                                                    output_type),
              "range": transform_schemaclasses_lst(se,
                                                   _prop.get("range"),
                                                   output_type),
              "curie": se.cls_converter.get_curie(_prop.get("uri")),
              "label": se.cls_converter.get_label(_prop.get("uri")),
              "uri": _prop.get("uri"),
              "object": se.get_property(_prop.get("uri"))} for _prop in prop_list]
    return props


def restructure_output(scls, response, func_name, output_type):
    if output_type == 'uri':
        if func_name in METHODS_RETURN_LIST:
            return list(response)
        elif func_name in METHODS_RETURN_DICT:
            return response
        elif func_name in METHODS_RETURN_STR:
            return response
    elif output_type == 'curie':
        if func_name in METHODS_RETURN_LIST:
            if func_name == 'parent_classes':
                return [list(map(scls.se.cls_converter.get_curie,
                                 _path)) for _path in response]
            elif func_name == 'list_properties':
                return [{'class': scls.se.cls_converter.get_curie(_item.get('class')),
                         'properties': transform_property_info_list(scls.se, _item.get('properties'), output_type)} for _item in response]
            elif func_name == "used_by":
                return transform_property_info_list(scls.se,
                                                    response,
                                                    output_type)
            else:
                return list(map(scls.se.cls_converter.get_curie,
                            response))
    elif output_type == 'label':
        if func_name in METHODS_RETURN_LIST:
            if func_name == 'parent_classes':
                return [list(map(scls.se.cls_converter.get_label,
                                 _path)) for _path in response]
            elif func_name == 'list_properties':
                return [{'class': scls.se.cls_converter.get_label(_item.get('class')),
                         'properties': transform_property_info_list(scls.se, _item.get('properties'), output_type)} for _item in response]
            elif func_name == "used_by":
                return transform_property_info_list(scls.se,
                                                    response,
                                                    output_type)
            else:
                return list(map(scls.se.cls_converter.get_label,
                                response))
    elif output_type == 'PythonClass':
        if func_name in METHODS_RETURN_LIST:
            if func_name == 'parent_classes':
                return [list(map(partial(SchemaClass, schema=scls.se),
                                 _path)) for _path in response]
            elif func_name == 'list_properties':
                return [{'class': SchemaClass(_item.get('class'), scls.se),
                         'properties': transform_property_info_list(scls.se, _item.get('properties'), output_type)} for _item in response]
            elif func_name == "used_by":
                return transform_property_info_list(scls.se,
                                                    response,
                                                    output_type)
            elif func_name in ['child_properties',
                               'parent_properties',
                               'descendant_properties']:
                return list(map(partial(SchemaProperty, schema=scls.se),
                            response))
            else:
                return list(map(partial(SchemaClass, schema=scls.se),
                            response))
    else:
        raise ValueError('output_type wrong. Should be one of uri, curie, label or PythonClass')


class Schema():
    """Class representing schema
    """
    # URI -> prefix conversion dict
    CONTEXT = {
        "schema": "http://schema.org/",
        "bts": "http://discovery.biothings.io/bts/"
    }

    def __init__(self, schema=None, context=None):
        self.default_schema_loaded = False
        self.context = self.CONTEXT
        if context:
            if not isinstance(context, dict):
                raise ValueError("context should be a python dictionary, with namespace/prefix as key, and URI as value")
            else:
                self.context.update(context)
        if not schema:
            self.load_default_schema()
        else:
            self.load_schema(schema)

    @property
    def validation(self):
        """ Parse validation info from schema file"""
        validation_info = {}
        for _doc in self.schema_extension_only['@graph']:
            if "$validation" in _doc:
                data = _doc["$validation"]
                # expand json schema definition from definitions field
                if "definitions" in _doc["$validation"]:
                    data = expand_ref(data, _doc["$validation"]["definitions"])
                validation_info[_doc["@id"]] = data
        for _doc in self.schema_extension_only["@graph"]:
            if "$validation" in _doc:
                # if json schema is not defined for a field, look for definition somewhere else
                for _item, _def in _doc['$validation']['properties'].items():
                    if type(_def) == dict and set(_def.keys()) == set(['description']):
                        sp = self.get_property(_item)
                        if type(sp) != list:
                            sp = [sp]
                        for _sp in sp:
                            for _range in _sp.range:
                                if _range.uri in validation_info:
                                    validation_info[_doc["@id"]]['properties'][_item].update(validation_info[_range.uri])
        return validation_info

    def load_schema(self, schema):
        """Load schema and convert it to networkx graph"""
        if not self.default_schema_loaded:
            self.load_default_schema()
        # load JSON-LD file of user defined schema
        self.schema_extension_only = preprocess_schema(load_json_or_yaml(schema))
        if "@context" in self.schema_extension_only:
            self.context.update(self.schema_extension_only["@context"])
        # convert user defined schema into a networkx DiGraph
        self.schema_extension_nx = load_schema_into_networkx(self.schema_extension_only)
        # update undefined classes/properties
        undefined_nodes = [node for node, attrdict in self.schema_extension_nx.node.items() if not attrdict]
        attr_dict = {}
        for _node in undefined_nodes:
            if _node in self.schemaorg_nx.nodes():
                attr_dict[_node] = self.schemaorg_nx.nodes[_node]
        nx.set_node_attributes(self.schema_extension_nx, attr_dict)
        # merge networkx graph of user-defined schema with networkx graph of schema defined by Schema.org
        self.schema_nx = merge_schema_networkx(self.schemaorg_nx, self.schema_extension_nx)
        SchemaValidator(self.schema_extension_only, self.schema_nx).validate_full_schema()
        # merge together the given schema and the schema defined by schemaorg
        self.schema = merge_schema(self.schema_extension_only,
                                   self.schemaorg_schema)
        # split the schema networkx into individual ones
        isolates = list(nx.isolates(self.schema_nx))
        self.extended_class_only_graph = self.schema_extension_nx.subgraph([node for node, attrdict in self.schema_extension_nx.node.items() if attrdict.get('type') == 'Class' and node not in isolates])
        self.full_class_only_graph = self.schema_nx.subgraph([node for node, attrdict in self.schema_nx.node.items() if attrdict.get('type') == 'Class'])
        self.property_only_graph = self.schema_nx.subgraph([node for node, attrdict in self.schema_nx.node.items() if attrdict.get('type') == 'Property'])
        # instantiate converters for classes and properties
        self._all_class_uris = [node for node,attrdict in self.schema_nx.node.items() if attrdict.get('type') in ['Class', 'DataType']]
        self.cls_converter = CurieUriConverter(self.context,
                                               self._all_class_uris)
        self._all_prop_uris = list(self.property_only_graph.nodes())
        self.prop_converter = CurieUriConverter(self.context,
                                                self._all_prop_uris)

    def load_default_schema(self):
        """Load default schema, either schema.org or biothings"""
        self.schema = preprocess_schema(load_schemaorg(version='8.0'))
        self.schemaorg_schema = self.schema
        if "@context" in self.schema:
            self.context.update(self.schema["@context"])
        self.schema_extension_only = self.schema
        self.schemaorg_nx = load_schema_into_networkx(self.schema)
        self.schema_extension_nx = self.schemaorg_nx
        self.schema_nx = self.schemaorg_nx
        isolates = list(nx.isolates(self.schema_nx))
        self.extended_class_only_graph = self.schema_extension_nx.subgraph([node for node, attrdict in self.schema_extension_nx.node.items() if attrdict['type'] == 'Class' and node not in isolates])
        self.full_class_only_graph = self.schema_nx.subgraph([node for node, attrdict in self.schema_nx.node.items() if attrdict['type'] == 'Class'])
        self.property_only_graph = self.schema_nx.subgraph([node for node, attrdict in self.schema_nx.node.items() if attrdict['type'] == 'Property'])
        # instantiate converters for classes and properties
        self._all_class_uris = [node for node,attrdict in self.schema_nx.node.items() if attrdict['type'] in ['Class', 'DataType']]
        self.cls_converter = CurieUriConverter(self.context,
                                               self._all_class_uris)
        self._all_prop_uris = list(self.property_only_graph.nodes())
        self.prop_converter = CurieUriConverter(self.context,
                                                self._all_prop_uris)
        self.default_schema_loaded = True

    def full_schema_graph(self, size=None):
        """Visualize the full schema loaded using graphviz"""
        edges = self.extended_class_only_graph.edges()
        curie_edges = []
        for _edge in edges:
            curie_edges.append((self.cls_converter.get_label(_edge[0]),
                                self.cls_converter.get_label(_edge[1])))
        return visualize(curie_edges, size=size)

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
            edges = list(nx.edge_bfs(self.full_class_only_graph,
                                     [self.cls_converter.get_uri(source)]))
        # handle cases where user want to get all parents
        elif include_parents and include_children is False:
            edges = []
            for _path in parents:
                _path.append(self.cls_converter.get_label(source))
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
        # handle cases where user want to get both parents and children
        elif include_parents and include_children:
            edges = list(nx.edge_bfs(self.full_class_only_graph,
                                     [self.cls_converter.get_uri(source)]))
            for _path in parents:
                _path.append(self.cls_converter.get_label(source))
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
        else:
            raise ValueError("At least one of include_parents and include_children parameter need to be set to True")
        curie_edges = []
        for _edge in edges:
            curie_edges.append((self.cls_converter.get_label(_edge[0]),
                                self.cls_converter.get_label(_edge[1])))
        return visualize(curie_edges, size=size)

    def list_all_classes(self):
        """Find all classes defined in the schema"""
        classes = list(self.extended_class_only_graph.nodes())
        classes = [SchemaClass(_cls, self) for _cls in classes]
        return classes

    def list_all_defined_classes(self):
        classes = [_item["@id"] for _item in self.schema_extension_only["@graph"] if "@type" in _item and _item["@type"] == "rdfs:Class" and _item["@id"] not in DATATYPES]
        classes = [SchemaClass(_cls, self) for _cls in classes]
        return classes

    def list_all_defined_properties(self):
        properties = [_item["@id"] for _item in self.schema_extension_only["@graph"] if "@type" in _item and _item["@type"] == "rdf:Property"]
        properties = [SchemaProperty(_cls, self) for _cls in properties]
        return properties

    def list_all_referenced_classes(self):
        all_classes = list(self.extended_class_only_graph.nodes())
        defined_classes = [_item["@id"] for _item in self.schema_extension_only["@graph"] if "@type" in _item and _item["@type"] == "rdfs:Class" and _item["@id"] not in DATATYPES]
        reference_classes = [SchemaClass(_cls, self) for _cls in (set(all_classes) - set(defined_classes))]
        return reference_classes

    def list_all_properties(self):
        """Find all properties defined in the schema"""
        properties = list(self.property_only_graph.nodes())
        properties = [SchemaProperty(_prop, self) for _prop in properties]
        return properties

    def get_class(self, class_name, output_type="PythonClass"):
        """Return a SchemaClass instance of the class"""
        uris = self.cls_converter.get_uri(class_name)
        if type(uris) == list:
            warnings.warn("Found more than 1 classes defined within schema using label {}".format(class_name))
            return [SchemaClass(_item, self, output_type) for _item in uris]
        else:
            return SchemaClass(class_name, self, output_type)

    def get_property(self, property_name, output_type="PythonClass"):
        """Return a SchemaProperty instance of the property"""
        uris = self.prop_converter.get_uri(property_name)
        if type(uris) == list:
            warnings.warn("Found more than 1 properties defined within schema using label {}".format(property_name))
            return [SchemaProperty(_item, self, output_type) for _item in uris]
        else:
            return SchemaProperty(property_name, self, output_type)

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
        self.load_schema(self.schema)
        print("Updated the class {} successfully!".format(class_info["rdfs:label"]))

    def update_property(self, property_info):
        """Add a new property into schema
        """
        SchemaValidator(self.schema_extension_only, self.full_schema_graph).validate_property_schema(property_info)
        self.schema["@graph"].append(property_info)
        self.load_schema(self.schema)
        print("Updated the property {} successfully!".format(property_info["rdfs:label"]))

    def export_schema(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.schema, f, sort_keys=True, indent=4,
                      ensure_ascii=False)


class SchemaClass():
    """Class representing an individual class in Schema
    """
    def __init__(self, class_name, schema, output_type='PythonClass'):
        self.defined_in_schema = True
        self.se = schema
        self.name = self.se.cls_converter.get_curie(class_name)
        # if class is not defined in schema, raise warning
        if self.uri not in self.se._all_class_uris:
            # raise ValueError('Class {} is not defined in Schema. Could not access it'.format(self.name))
            warnings.warn('Class {} is not defined in Schema. Could not access it'.format(self.name))
            self.defined_in_schema = False
        self.output_type = output_type

    def __repr__(self):
        return '<SchemaClass "' + self.name + '">'

    def __str__(self):
        return str(self.name)

    @property
    def prefix(self):
        return self.se.cls_converter.get_prefix(self.name)

    @property
    def label(self):
        return self.se.cls_converter.get_label(self.name)

    @property
    def uri(self):
        return self.se.cls_converter.get_uri(self.name)

    @property
    def description(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        # classes might not have descriptions
        if 'description' in self.se.full_class_only_graph.node[self.uri]:
            return self.se.schema_nx.node[self.uri]['description']
        else:
            return None

    @property
    def child_classes(self):
        """Find schema classes that directly inherit from the given class
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        children = self.se.full_class_only_graph.successors(self.uri)
        result = restructure_output(self,
                                    children,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    @property
    def descendant_classes(self):
        """Find schema classes that inherit from the given class
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        descendants = nx.descendants(self.se.full_class_only_graph,
                                     self.uri)
        result = restructure_output(self,
                                    descendants,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    @property
    def ancestor_classes(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        ancestors = nx.ancestors(self.se.full_class_only_graph, self.uri)
        result = restructure_output(self,
                                    ancestors,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    @property
    def parent_classes(self):
        """Find all parents of a specific class"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        root_node = list(nx.topological_sort(self.se.full_class_only_graph))
        # When a schema is not a tree with only one root node
        # Set "Thing" as the root node by default
        if 'http://schema.org/Thing' in root_node:
            root_node = 'http://schema.org/Thing'
        else:
            root_node = root_node[0]
        paths = nx.all_simple_paths(self.se.full_class_only_graph,
                                    source=root_node,
                                    target=self.uri)
        paths =  [_path[:-1] for _path in paths]
        result = restructure_output(self,
                                    paths,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    def list_properties(self, class_specific=True, group_by_class=True):
        """Find properties of a class

        :arg boolean class_specific: specify whether only to return class specific properties or not
        :arg boolean group_by_class: specify whether the output should be grouped by class or not
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        properties = [{'class': self.name,
                       'properties': self.se.full_class_only_graph.nodes[self.uri]['properties']}]
        if not class_specific:
            # find all parent classes
            if self.output_type == "PythonClass":
                parents = [_item.uri for _item in self.ancestor_classes]
            else:
                parents = [self.se.cls_converter.get_uri(_item) for _item in self.ancestor_classes]
            # update properties, each dict represent properties associated with the class
            for _parent in parents:
                properties.append({
                    "class": _parent,
                    "properties": self.se.full_class_only_graph.nodes[_parent]['properties']
                })
        result = restructure_output(self,
                                    properties,
                                    inspect.stack()[0][3],
                                    self.output_type)
        if group_by_class:
            return result
        else:
            ungrouped_properties = []
            for _item in result:
                ungrouped_properties += _item['properties']
            return ungrouped_properties

    def used_by(self):
        """Find where a given class is used as a value of a property"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        if 'used_by' in self.se.full_class_only_graph.nodes[self.uri]:
            response = self.se.full_class_only_graph.nodes[self.uri]['used_by']
            result = restructure_output(self,
                                        response,
                                        inspect.stack()[0][3],
                                        self.output_type)
            return result
        else:
            return []

    @property
    def validation(self):
        return self.se.validation.get(self.uri)

    def describe(self):
        """Find details about a specific schema class
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        class_info = {'properties': self.list_properties(class_specific=False),
                      'description': self.description,
                      'uri': self.uri,
                      'label': self.label,
                      'curie': self.name,
                      'used_by': self.used_by(),
                      'child_classes': self.child_classes,
                      'parent_classes': self.parent_classes,
                      'ancestor_classes': self.ancestor_classes,
                      'descendant_classes': self.descendant_classes,
                      'validation': self.validation}
        return class_info

    def validate_against_schema(self, json_doc):
        """Validate a json document against it's JSON schema defined in Schema

        :arg dict json_doc: The JSON Document to be validated
        :arg str class_uri: The URI of the class which has JSON schema
        """
        if self.uri not in self.se.validation:
            raise RuntimeError("$validation is not defined for {} field; thus the json document could not be validated".format(self.name))
        else:
            validate(json_doc, self.se.validation[self.uri], format_checker=jsonschema.FormatChecker())
            print('The JSON document is valid')


class SchemaProperty():
    """Class representing an individual property in Schema
    """

    def __init__(self, property_name, schema, output_type="PythonClass"):
        self.defined_in_schema = True
        self.se = schema
        self.name = self.se.prop_converter.get_curie(property_name)
        # if property is not defined in schema, raise ValueError
        if self.uri not in self.se.property_only_graph:
            #raise ValueError('Property {} is not defined in Schema. Could not access it'.format(self.name))
            warnings.warn('Property {} is not defined in Schema. Could not access it'.format(self.name))
            self.defined_in_schema = False
        self.output_type = output_type

    def __repr__(self):
        return '<SchemaProperty "' + self.name + '"">'

    def __str__(self):
        return str(self.name)

    @property
    def domain(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        if 'domain' in self.se.property_only_graph.nodes[self.uri]:
            _domain = self.se.property_only_graph.nodes[self.uri]['domain']
            result = restructure_output(self,
                                        _domain,
                                        inspect.stack()[0][3],
                                        self.output_type)
            return result
        else:
            return []

    @property
    def range(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        if 'range' in self.se.property_only_graph.nodes[self.uri]:
            _range = self.se.property_only_graph.nodes[self.uri]['range']
            result = restructure_output(self,
                                        _range,
                                        inspect.stack()[0][3],
                                        self.output_type)
            return result
        else:
            return []

    @property
    def prefix(self):
        return self.se.prop_converter.get_prefix(self.name)

    @property
    def label(self):
        return self.se.prop_converter.get_label(self.name)

    @property
    def uri(self):
        return self.se.prop_converter.get_uri(self.name)

    @property
    def description(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        # some properties doesn't have descriptions
        if 'description' in self.se.property_only_graph.node[self.uri]:
            return self.se.property_only_graph.node[self.uri]['description']
        else:
            return None

    @property
    def parent_properties(self):
        """Find all parents of a specific class"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        parents = nx.ancestors(self.se.property_only_graph,
                               self.uri)
        result = restructure_output(self,
                                    parents,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    @property
    def child_properties(self):
        """Find schema properties that directly inherit from the given property
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        children = self.se.property_only_graph.successors(self.uri)
        result = restructure_output(self,
                                    children,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    @property
    def descendant_properties(self):
        """Find schema properties that inherit from the given property
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        descendants = nx.descendants(self.se.property_only_graph,
                                     self.uri)
        result = restructure_output(self,
                                    descendants,
                                    inspect.stack()[0][3],
                                    self.output_type)
        return result

    @property
    def inverse_property(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        inverse = self.se.property_only_graph.node[self.uri]['inverse']
        if not inverse:
            return inverse
        else:
            return self.se.get_property(inverse)

    def describe(self):
        """Find details about a specific property
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        property_info = {'child_properties': self.child_properties,
                         'descendant_properties': self.descendant_properties,
                         'parent_properties': self.parent_properties,
                         'domain': self.domain,
                         'range': self.range,
                         'uri': self.uri,
                         'label': self.label,
                         'description': self.description}
        return property_info


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
        self.schemaorg = {'schema': load_schemaorg(version='8.0'),
                          'classes': [],
                          'properties': []}
        for _record in self.schemaorg['schema']['@graph']:
            if "@type" in _record:
                _type = str2list(_record["@type"])
                if "rdfs:Property" in _type:
                    self.schemaorg['properties'].append(_record["@id"])
                elif "rdfs:Class" in _type:
                    self.schemaorg['classes'].append(_record["@id"])
        self.extension_schema = {'schema': preprocess_schema(schema),
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
                # raise KeyError('Value of rangeincludes: {} is not defined in the schema.'.format(record["@id"]))
                pass

    def check_whether_atid_and_label_match(self, record):
        """ Check if @id field matches with the "rdfs:label" field
        """
        _id = extract_name_from_uri_or_curie(record["@id"])
        if _id != record["rdfs:label"]:
            raise ValueError("id and label not match: {}".format(record))

    """
    def check_duplicate_labels(self):
        #Check for duplication in the schema
        labels = [_record['rdfs:label'] for _record in self.extension_schema["schema"]["@graph"]]
        duplicates = find_duplicates(labels)
        if duplicates:
            raise ValueError('Duplicates detected in graph: {}'.format(duplicates))
    """

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
                                            source='http://schema.org/Thing',
                                            target=schema["@id"])
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
                                if record["@id"] in parent_classes:
                                    matched = True
                    if not matched:
                        raise ValueError('field {} in $validation is not correctly documented'.format(_property))
        else:
            pass

    def validate_full_schema(self):
        """ Main function to validate schema
        """
        #self.check_duplicate_labels()
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
            #else:
                # raise ValueError('wrong @type value found: {}'.format(record))
