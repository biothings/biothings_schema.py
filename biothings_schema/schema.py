import inspect
import json
import warnings
from functools import partial

import networkx as nx
from jsonschema import FormatChecker, validate

from .base import visualize
from .curies import CurieUriConverter, preprocess_schema
from .dataload import BaseSchemaLoader, load_json_or_yaml, load_schema_into_networkx
from .settings import (
    COMMON_NAMESPACES,
    DATATYPES,
    DEFAULT_JSONSCHEMA_METASCHEMA,
    VALIDATION_FIELD,
)  # ALT_VALIDATION_FIELDS,
from .utils import expand_ref, merge_schema, merge_schema_networkx
from .validator import SchemaValidator

METHODS_RETURN_LIST = [
    "ancestor_classes",
    "child_classes",
    "descendant_classes",
    "parent_classes",
    "list_properties",
    "used_by",
    "domain",
    "range",
    "parent_properties",
    "child_properties",
    "descendant_properties",
]

METHODS_RETURN_DICT = ["describe"]

METHODS_RETURN_STR = ["description", "label", "prefix", "uri", "inverse_property"]


def check_defined(scls, method_name):
    if not scls.defined_in_schema:
        if method_name in METHODS_RETURN_LIST:
            return []
        elif method_name in METHODS_RETURN_STR:
            return ""
        elif method_name in METHODS_RETURN_DICT:
            return {}
    else:
        return scls.defined_in_schema


def transform_schemaclasses_lst(se, scls_list, output_type):
    """Transform a list of schemaclass classes"""
    if output_type == "uri":
        return scls_list
    elif output_type == "curie":
        return list(map(se.cls_converter.get_curie, scls_list))
    elif output_type == "label":
        return list(map(se.cls_converter.get_label, scls_list))
    elif output_type == "PythonClass":
        return list(map(partial(SchemaClass, schema=se), scls_list))
    else:
        raise ValueError(
            'Invalid "output_type" value. Should be one of "uri", "curie", "label" or "PythonClass"'
        )


def transform_property_info_list(se, prop_list, output_type):
    """Transform a list of properties"""
    props = [
        {
            "description": _prop.get("description"),
            "domain": transform_schemaclasses_lst(se, _prop.get("domain"), output_type),
            "range": transform_schemaclasses_lst(se, _prop.get("range"), output_type),
            "curie": se.cls_converter.get_curie(_prop.get("uri")),
            "label": se.cls_converter.get_label(_prop.get("uri")),
            "uri": _prop.get("uri"),
            "object": se.get_property(_prop.get("uri")),
        }
        for _prop in prop_list
    ]
    return props


def restructure_output(scls, response, func_name, output_type):
    if output_type == "uri":
        if func_name in METHODS_RETURN_LIST:
            return list(response)
        elif func_name in METHODS_RETURN_DICT:
            return response
        elif func_name in METHODS_RETURN_STR:
            return response
    elif output_type == "curie":
        if func_name in METHODS_RETURN_LIST:
            if func_name == "parent_classes":
                return [list(map(scls.se.cls_converter.get_curie, _path)) for _path in response]
            elif func_name == "list_properties":
                return [
                    {
                        "class": scls.se.cls_converter.get_curie(_item.get("class")),
                        "properties": transform_property_info_list(
                            scls.se, _item.get("properties"), output_type
                        ),
                    }
                    for _item in response
                ]
            elif func_name == "used_by":
                return transform_property_info_list(scls.se, response, output_type)
            else:
                return list(map(scls.se.cls_converter.get_curie, response))
    elif output_type == "label":
        if func_name in METHODS_RETURN_LIST:
            if func_name == "parent_classes":
                return [list(map(scls.se.cls_converter.get_label, _path)) for _path in response]
            elif func_name == "list_properties":
                return [
                    {
                        "class": scls.se.cls_converter.get_label(_item.get("class")),
                        "properties": transform_property_info_list(
                            scls.se, _item.get("properties"), output_type
                        ),
                    }
                    for _item in response
                ]
            elif func_name == "used_by":
                return transform_property_info_list(scls.se, response, output_type)
            else:
                return list(map(scls.se.cls_converter.get_label, response))
    elif output_type == "PythonClass":
        if func_name in METHODS_RETURN_LIST:
            if func_name == "parent_classes":
                return [
                    list(map(partial(SchemaClass, schema=scls.se), _path)) for _path in response
                ]
            elif func_name == "list_properties":
                return [
                    {
                        "class": SchemaClass(_item.get("class"), scls.se),
                        "properties": transform_property_info_list(
                            scls.se, _item.get("properties"), output_type
                        ),
                    }
                    for _item in response
                ]
            elif func_name == "used_by":
                return transform_property_info_list(scls.se, response, output_type)
            elif func_name in ["child_properties", "parent_properties", "descendant_properties"]:
                return list(map(partial(SchemaProperty, schema=scls.se), response))
            else:
                return list(map(partial(SchemaClass, schema=scls.se), response))
    else:
        raise ValueError("output_type wrong. Should be one of uri, curie, label or PythonClass")


class Schema:
    """Class representing schema"""

    # URI -> prefix conversion dict
    DEFAULT_CONTEXT = {"schema": "http://schema.org/"}

    def __init__(
        self,
        schema=None,
        context=None,
        base_schema=None,
        validator_options=None,
        base_schema_loader=None,
    ):
        self.validator_options = validator_options or {}
        self.base_schema_loaded = False
        self.schema = None
        self.validator = None
        self.base_schema_loader = base_schema_loader or BaseSchemaLoader()
        _schema = load_json_or_yaml(schema) if schema else {}
        # self.context = self.CONTEXT
        self.context = _schema.get("@context", {})
        if context:
            if not isinstance(context, dict):
                raise ValueError(
                    "context should be a python dictionary, with namespace/prefix as key, and URI as value"
                )
            else:
                self.context.update(context)
        # make sure self.context includes at least schema.org namespace
        self.context.setdefault("schema", self.DEFAULT_CONTEXT["schema"])
        self.namespace = self.get_schema_namespace(_schema)
        base_schema = base_schema or self.get_base_schema_list(_schema)
        # print(self.namespace, base_schema)
        self.load_schema(schema=_schema, base_schema=base_schema)

    @property
    def validation(self):
        """Parse validation info from schema file"""
        validation_info = {}
        for _doc in self.schema["@graph"]:
            if VALIDATION_FIELD in _doc:
                data = _doc[VALIDATION_FIELD]
                if "$schema" not in data:
                    # add missing metaschema specified by $schema
                    data["$schema"] = DEFAULT_JSONSCHEMA_METASCHEMA
                # expand json schema definition from definitions field
                if "definitions" in _doc[VALIDATION_FIELD]:
                    data = expand_ref(data, _doc[VALIDATION_FIELD]["definitions"])
                validation_info[_doc["@id"]] = data

        # NOTE: the reference of "validation_info[_range.uri]" below causes circular reference,
        #       also this block of code does not seems relevant any more. validation schemas from
        #       the parent classes are now premerged in Validator class.
        # for _doc in self.schema["@graph"]:
        #     if VALIDATION_FIELD in _doc:
        #         # if json schema is not defined for a field, look for definition somewhere else
        #         for _item, _def in _doc[VALIDATION_FIELD]['properties'].items():
        #             if type(_def) == dict and set(_def.keys()) == set(['description']):
        #                 sp = self.get_property(_item)
        #                 if type(sp) != list:
        #                     sp = [sp]
        #                 for _sp in sp:
        #                     for _range in _sp.range:
        #                         if _range.uri in validation_info:
        #                             validation_info[_doc["@id"]]['properties'][_item].update(validation_info[_range.uri])
        return validation_info

    def load_schema(self, schema=None, base_schema=None):
        """Load schema and convert it to networkx graph"""
        if not self.base_schema_loaded:
            self.load_base_schema(base_schema=base_schema)

        if schema:
            # load JSON-LD file of user defined schema
            self.schema = preprocess_schema(load_json_or_yaml(schema))
        else:
            # set to an empty schema dictionary
            self.schema = {"@context": {}, "@graph": []}

        if "@context" in self.schema:
            self.context.update(self.schema["@context"])
        # convert user defined schema into a networkx DiGraph
        self.schema_nx = load_schema_into_networkx(self.schema)
        # update undefined classes/properties
        undefined_nodes = [
            node for node, attrdict in self.schema_nx.nodes._nodes.items() if not attrdict
        ]
        attr_dict = {}
        for _node in undefined_nodes:
            if _node in self.base_schema_nx.nodes():
                attr_dict[_node] = self.base_schema_nx.nodes[_node]
        nx.set_node_attributes(self.schema_nx, attr_dict)
        self.full_schema = merge_schema(self.base_schema, self.schema)
        self.full_schema_nx = merge_schema_networkx(self.base_schema_nx, self.schema_nx)
        self.validator = SchemaValidator(
            self.schema, self.full_schema_nx, self.base_schema, **self.validator_options
        )
        self.validator.validate_full_schema()

        # split the schema networkx into individual ones
        isolates = list(nx.isolates(self.full_schema_nx))
        self.extended_class_only_graph = self.schema_nx.subgraph(
            [
                node
                for node, attrdict in self.schema_nx.nodes._nodes.items()
                if attrdict.get("type") == "Class" and node not in isolates
            ]
        )
        self.full_class_only_graph = self.full_schema_nx.subgraph(
            [
                node
                for node, attrdict in self.full_schema_nx.nodes._nodes.items()
                if attrdict.get("type") == "Class"
            ]
        )
        self.property_only_graph = self.full_schema_nx.subgraph(
            [
                node
                for node, attrdict in self.full_schema_nx.nodes._nodes.items()
                if attrdict.get("type") == "Property"
            ]
        )
        # instantiate converters for classes and properties
        self._all_class_uris = [
            node
            for node, attrdict in self.full_schema_nx.nodes._nodes.items()
            if attrdict.get("type") in ["Class", "DataType"]
        ]
        self.cls_converter = CurieUriConverter(self.context, self._all_class_uris)
        self._all_prop_uris = list(self.property_only_graph.nodes())
        self.prop_converter = CurieUriConverter(self.context, self._all_prop_uris)

    def get_schema_namespace(self, schema):
        """
        Get the namespace defined in a given schema
        It checks the prefix of @id fields of each defined classes and properies
        If the prefixes are not consistent (>1 namespace), None is returned
        with a warning message.
        """
        if isinstance(schema, dict) and "@graph" in schema:
            namespace_set = list(
                set([_doc["@id"].split(":", maxsplit=1)[0] for _doc in schema["@graph"]])
            )
            if len(namespace_set) == 1:
                return namespace_set[0]
            else:
                warnings.warn(
                    f"Found multiple namespace prefixes defined in the schema: f{namespace_set}"
                )

    def get_base_schema_list(self, schema, include_current=True):
        """
        Get the list of referenced base schemas based on the "@context" field
        """
        _base_schema = [
            namespace for namespace in self.context if namespace not in COMMON_NAMESPACES
        ]
        if not include_current:
            _current_namespace = self.get_schema_namespace(schema)
            if _current_namespace in _base_schema:
                _base_schema.remove(_current_namespace)
        return _base_schema

    def load_base_schema(self, base_schema=None):
        """
        Load base schema, defined in self.BASE_SCHEMA,
        but can be override in `base_schema` parameter.
        """
        _base_schema = self.base_schema_loader.load(base_schema=base_schema)
        self.base_schema = preprocess_schema(_base_schema)
        self.base_schema_nx = load_schema_into_networkx(self.base_schema)
        self.base_schema_loaded = True

    def full_schema_graph(self, size=None):
        """Visualize the full schema loaded using graphviz"""
        edges = self.extended_class_only_graph.edges()
        curie_edges = []
        for _edge in edges:
            curie_edges.append(
                (self.cls_converter.get_label(_edge[0]), self.cls_converter.get_label(_edge[1]))
            )
        return visualize(curie_edges, size=size)

    def sub_schema_graph(self, source, include_parents=True, include_children=True, size=None):
        """Visualize a sub-graph of the schema based on a specific node"""
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
            edges = list(
                nx.edge_bfs(self.full_class_only_graph, [self.cls_converter.get_uri(source)])
            )
        # handle cases where user want to get all parents
        elif include_parents and include_children is False:
            edges = []
            for _path in parents:
                _path.append(self.cls_converter.get_label(source))
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
        # handle cases where user want to get both parents and children
        elif include_parents and include_children:
            edges = list(
                nx.edge_bfs(self.full_class_only_graph, [self.cls_converter.get_uri(source)])
            )
            for _path in parents:
                _path.append(self.cls_converter.get_label(source))
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
        else:
            raise ValueError(
                "At least one of include_parents and include_children parameter need to be set to True"
            )
        curie_edges = []
        for _edge in edges:
            curie_edges.append(
                (self.cls_converter.get_label(_edge[0]), self.cls_converter.get_label(_edge[1]))
            )
        return visualize(curie_edges, size=size)

    def list_all_classes(self, include_base=False):
        """Find all classes defined in the schema
        if "include_base" is True, it return every classes from the base_schema
        (e.g. schema.org)
        """
        _graph = self.full_class_only_graph if include_base else self.extended_class_only_graph
        classes = [SchemaClass(_cls, self) for _cls in _graph.nodes()]
        return classes

    def list_all_defined_classes(self):
        classes = [
            _item["@id"]
            for _item in self.schema["@graph"]
            if "@type" in _item
            and _item["@type"] == "rdfs:Class"
            and _item["@id"] not in DATATYPES
        ]
        classes = [SchemaClass(_cls, self) for _cls in classes]
        return classes

    def list_all_defined_properties(self):
        properties = [
            _item["@id"]
            for _item in self.schema["@graph"]
            if "@type" in _item and _item["@type"] == "rdf:Property"
        ]
        properties = [SchemaProperty(_cls, self) for _cls in properties]
        return properties

    def list_all_referenced_classes(self):
        all_classes = list(self.extended_class_only_graph.nodes())
        defined_classes = [
            _item["@id"]
            for _item in self.schema["@graph"]
            if "@type" in _item
            and _item["@type"] == "rdfs:Class"
            and _item["@id"] not in DATATYPES
        ]
        reference_classes = [
            SchemaClass(_cls, self) for _cls in (set(all_classes) - set(defined_classes))
        ]
        return reference_classes

    def list_all_properties(self):
        """Find all properties defined in the schema"""
        properties = list(self.property_only_graph.nodes())
        properties = [SchemaProperty(_prop, self) for _prop in properties]
        return properties

    def get_class(self, class_name, output_type="PythonClass"):
        """Return a SchemaClass instance of the class"""
        uris = self.cls_converter.get_uri(class_name)
        if isinstance(uris, list):
            warnings.warn(
                "Found more than 1 classes defined within schema using label {}".format(class_name)
            )
            return [SchemaClass(_item, self, output_type) for _item in uris]
        else:
            return SchemaClass(class_name, self, output_type)

    def get_property(self, property_name, output_type="PythonClass"):
        """Return a SchemaProperty instance of the property"""
        uris = self.prop_converter.get_uri(property_name)
        if isinstance(uris, list):
            warnings.warn(
                "Found more than 1 properties defined within schema using label {}".format(
                    property_name
                )
            )
            return [SchemaProperty(_item, self, output_type) for _item in uris]
        else:
            return SchemaProperty(property_name, self, output_type)

    def generate_class_template(self):
        """Generate a template for schema class"""
        template = {
            "@id": "uri or curie of the class",
            "@type": "rdfs:Class",
            "rdfs:comment": "description of the class",
            "rdfs:label": "class label, should match @id",
            "rdfs:subClassOf": {"@id": "parent class, could be list"},
            "schema:isPartOf": {"@id": "http://schema.biothings.io"},
        }
        return template

    def generate_property_template(self):
        """Generate a template for schema property"""
        template = {
            "@id": "url or curie of the property",
            "@type": "rdf:Property",
            "rdfs:comment": "description of the property",
            "rdfs:label": "carmel case, should match @id",
            "schema:domainIncludes": {"@id": "class which use it as a property, could be list"},
            "schema:isPartOf": {"@id": "http://schema.biothings.io"},
            "schema:rangeIncludes": {
                "@id": "relates a property to a class that constitutes (one of) the expected type(s) for values of the property"
            },
        }
        return template

    def update_class(self, class_info):
        """Add a new class into schema"""
        self.validator.validate_class_schema(class_info)
        self.schema["@graph"].append(class_info)
        self.load_schema(self.schema)
        print("Updated the class {} successfully!".format(class_info["rdfs:label"]))

    def update_property(self, property_info):
        """Add a new property into schema"""
        self.validator.validate_property_schema(property_info)
        self.schema["@graph"].append(property_info)
        self.load_schema(self.schema)
        print("Updated the property {} successfully!".format(property_info["rdfs:label"]))

    def export_schema(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.schema, f, sort_keys=True, indent=4, ensure_ascii=False)


class SchemaClass:
    """Class representing an individual class in Schema"""

    def __init__(self, class_name, schema, output_type="PythonClass"):
        self.defined_in_schema = True
        self.se = schema
        self.name = self.se.cls_converter.get_curie(class_name)
        # if class is not defined in schema, raise warning
        if self.uri not in self.se._all_class_uris:
            # raise ValueError('Class {} is not defined in Schema. Could not access it'.format(self.name))
            warnings.warn(
                "Class {} is not defined in Schema. Could not access it".format(self.name)
            )
            self.defined_in_schema = False
        self.output_type = output_type

    def __repr__(self):
        return f'<SchemaClass "{self.name}">'

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
        if "description" in self.se.full_class_only_graph.nodes._nodes[self.uri]:
            return self.se.full_schema_nx.nodes._nodes[self.uri]["description"]
        else:
            return None

    @property
    def child_classes(self):
        """Find schema classes that directly inherit from the given class"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        children = self.se.full_class_only_graph.successors(self.uri)
        result = restructure_output(self, children, inspect.stack()[0][3], self.output_type)
        return result

    @property
    def descendant_classes(self):
        """Find schema classes that inherit from the given class"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        descendants = nx.descendants(self.se.full_class_only_graph, self.uri)
        result = restructure_output(self, descendants, inspect.stack()[0][3], self.output_type)
        return result

    @property
    def ancestor_classes(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        ancestors = nx.ancestors(self.se.full_class_only_graph, self.uri)
        result = restructure_output(self, ancestors, inspect.stack()[0][3], self.output_type)
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
        if "http://schema.org/Thing" in root_node:
            root_node = "http://schema.org/Thing"
        else:
            root_node = root_node[0]
        paths = nx.all_simple_paths(
            self.se.full_class_only_graph, source=root_node, target=self.uri
        )
        paths = [_path[:-1] for _path in paths]
        result = restructure_output(self, paths, inspect.stack()[0][3], self.output_type)
        return result

    def list_properties(self, class_specific=True, group_by_class=True):
        """Find properties of a class

        :arg boolean class_specific: specify whether only to return class specific properties or not
        :arg boolean group_by_class: specify whether the output should be grouped by class or not
        """
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        properties = [
            {
                "class": self.name,
                "properties": self.se.full_class_only_graph.nodes[self.uri]["properties"],
            }
        ]
        if not class_specific:
            # find all parent classes
            if self.output_type == "PythonClass":
                parents = [_item.uri for _item in self.ancestor_classes]
            else:
                parents = [self.se.cls_converter.get_uri(_item) for _item in self.ancestor_classes]
            # update properties, each dict represent properties associated with the class
            for _parent in parents:
                properties.append(
                    {
                        "class": _parent,
                        "properties": self.se.full_class_only_graph.nodes[_parent]["properties"],
                    }
                )
        result = restructure_output(self, properties, inspect.stack()[0][3], self.output_type)
        if group_by_class:
            return result
        else:
            ungrouped_properties = []
            for _item in result:
                ungrouped_properties += _item["properties"]
            return ungrouped_properties

    def used_by(self):
        """Find where a given class is used as a value of a property"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        if "used_by" in self.se.full_class_only_graph.nodes[self.uri]:
            response = self.se.full_class_only_graph.nodes[self.uri]["used_by"]
            result = restructure_output(self, response, inspect.stack()[0][3], self.output_type)
            return result
        else:
            return []

    @property
    def validation(self):
        return self.se.validation.get(self.uri)

    def describe(self):
        """Find details about a specific schema class"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        class_info = {
            "properties": self.list_properties(class_specific=False),
            "description": self.description,
            "uri": self.uri,
            "label": self.label,
            "curie": self.name,
            "used_by": self.used_by(),
            "child_classes": self.child_classes,
            "parent_classes": self.parent_classes,
            "ancestor_classes": self.ancestor_classes,
            "descendant_classes": self.descendant_classes,
            "validation": self.validation,
        }
        return class_info

    def validate_against_schema(self, json_doc):
        """Validate a json document against it's JSON schema defined in Schema

        :arg dict json_doc: The JSON Document to be validated
        :arg str class_uri: The URI of the class which has JSON schema
        """
        if self.uri not in self.se.validation:
            raise RuntimeError(
                f"{VALIDATION_FIELD} is not defined for {self.name} field; thus the json document could not be validated"
            )
        else:
            validate(json_doc, self.se.validation[self.uri], format_checker=FormatChecker())
            print("The JSON document is valid")


class SchemaProperty:
    """Class representing an individual property in Schema"""

    def __init__(self, property_name, schema, output_type="PythonClass"):
        self.defined_in_schema = True
        self.se = schema
        self.name = self.se.prop_converter.get_curie(property_name)
        # if property is not defined in schema, raise ValueError
        if self.uri not in self.se.property_only_graph:
            # raise ValueError('Property {} is not defined in Schema. Could not access it'.format(self.name))
            warnings.warn(
                "Property {} is not defined in Schema. Could not access it".format(self.name)
            )
            self.defined_in_schema = False
        self.output_type = output_type

    def __repr__(self):
        return f'<SchemaProperty "{self.name}">'

    def __str__(self):
        return str(self.name)

    @property
    def domain(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        if "domain" in self.se.property_only_graph.nodes[self.uri]:
            _domain = self.se.property_only_graph.nodes[self.uri]["domain"]
            result = restructure_output(self, _domain, inspect.stack()[0][3], self.output_type)
            return result
        else:
            return []

    @property
    def range(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        if "range" in self.se.property_only_graph.nodes[self.uri]:
            _range = self.se.property_only_graph.nodes[self.uri]["range"]
            result = restructure_output(self, _range, inspect.stack()[0][3], self.output_type)
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
        if "description" in self.se.property_only_graph.nodes._nodes[self.uri]:
            return self.se.property_only_graph.nodes._nodes[self.uri]["description"]
        else:
            return None

    @property
    def parent_properties(self):
        """Find all parents of a specific class"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        parents = nx.ancestors(self.se.property_only_graph, self.uri)
        result = restructure_output(self, parents, inspect.stack()[0][3], self.output_type)
        return result

    @property
    def child_properties(self):
        """Find schema properties that directly inherit from the given property"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        children = self.se.property_only_graph.successors(self.uri)
        result = restructure_output(self, children, inspect.stack()[0][3], self.output_type)
        return result

    @property
    def descendant_properties(self):
        """Find schema properties that inherit from the given property"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        descendants = nx.descendants(self.se.property_only_graph, self.uri)
        result = restructure_output(self, descendants, inspect.stack()[0][3], self.output_type)
        return result

    @property
    def inverse_property(self):
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        inverse = self.se.property_only_graph.node[self.uri]["inverse"]
        if not inverse:
            return inverse
        else:
            return self.se.get_property(inverse)

    def describe(self):
        """Find details about a specific property"""
        response = check_defined(self, inspect.stack()[0][3])
        if not response:
            return response
        property_info = {
            "child_properties": self.child_properties,
            "descendant_properties": self.descendant_properties,
            "parent_properties": self.parent_properties,
            "domain": self.domain,
            "range": self.range,
            "uri": self.uri,
            "label": self.label,
            "description": self.description,
        }
        return property_info
