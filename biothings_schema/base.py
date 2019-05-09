import json
import urllib.request
import os
from functools import wraps

import networkx as nx
from jsonschema import validate

_ROOT = os.path.abspath(os.path.dirname(__file__))


def load_json(file_path):
    """Load json document from file path or url

    :arg str file_path: The path of the url doc, could be url or file path
    """
    # handle url
    if file_path.startswith("http"):
        with urllib.request.urlopen(file_path) as url:
            data = json.loads(url.read().decode())
            return data
    # handle file path
    else:
        with open(file_path) as f:
            data = json.load(f)
            return data


def export_json(json_doc, file_path):
    """Export JSON doc to file
    """
    with open(file_path, 'w') as f:
        json.dump(json_doc, f, sort_keys=True,
                  indent=4, ensure_ascii=False)


def load_default():
    """Load biolink vocabulary
    """
    biothings_path = os.path.join(_ROOT, 'data', 'biothings.jsonld')
    return load_json(biothings_path)


def load_schemaorg():
    """Load SchemOrg vocabulary
    """
    schemaorg_path = os.path.join(_ROOT, 'data', 'all_layer.jsonld')
    return load_json(schemaorg_path)


def validate_schema(schema):
    """Validate schema against SchemaORG standard
    """
    json_schema_path = os.path.join(_ROOT, 'data', 'schema.json')
    json_schema = load_json(json_schema_path)
    return validate(schema, json_schema)


def validate_property_schema(schema):
    """Validate schema against SchemaORG property definition standard
    """
    json_schema_path = os.path.join(_ROOT, 'data', 'property_json_schema.json')
    json_schema = load_json(json_schema_path)
    return validate(schema, json_schema)


def validate_class_schema(schema):
    """Validate schema against SchemaORG class definition standard
    """
    json_schema_path = os.path.join(_ROOT, 'data', 'class_json_schema.json')
    json_schema = load_json(json_schema_path)
    return validate(schema, json_schema)


def extract_name_from_uri_or_curie(item):
    """Extract name from uri or curie
    """
    if 'http' not in item and len(item.split(":")) == 2:
        return item.split(":")[-1]
    elif len(item.split("//")[-1].split('/')) > 1:
        return item.split("//")[-1].split('/')[-1]
    else:
        print("error")


def load_schema_into_networkx(schema):
    G = nx.DiGraph()
    CLASS_REMOVE = ["http://schema.org/Number",
                    "http://schema.org/Integer",
                    "http://schema.org/Float",
                    "http://schema.org/Text",
                    "http://schema.org/CssSelectorType",
                    "http://schema.org/URL",
                    "http://schema.org/XPathType"]
    for record in schema["@graph"]:
        if record["@type"] == "rdfs:Class" and record["@id"] not in CLASS_REMOVE:
            G.add_node(extract_name_from_uri_or_curie(record["@id"]),
                       uri=record["@id"],
                       description=record["rdfs:comment"])
            if "rdfs:subClassOf" in record:
                parents = record["rdfs:subClassOf"]
                if isinstance(parents, list):
                    for _parent in parents:
                        G.add_edge(extract_name_from_uri_or_curie(_parent["@id"]),
                                   extract_name_from_uri_or_curie(record["@id"]))
                elif isinstance(parents, dict):
                    G.add_edge(extract_name_from_uri_or_curie(parents["@id"]),
                               extract_name_from_uri_or_curie(record["@id"]))
    return G


def dict2list(dictionary):
    if isinstance(dictionary, list):
        return dictionary
    elif isinstance(dictionary, dict):
        return [dictionary]


def str2list(_str):
    if isinstance(_str, str):
        return [_str]
    elif isinstance(_str, list):
        return _str
    else:
        raise ValueError('"_str" input is not a str or list')


def unlist(_list):
    if len(_list) == 1:
        return _list[0]
    else:
        return _list


def require_optional(*module_list):
    """ A decorator to make sure an optional module(s) is imported,
        otherwise, print out proper error msg.

            @require_optional('graphviz')
            def a_func(): pass
        or
            @require_optional('graphviz', 'pkg2', 'pkg3.mod1')
            def a_func(): pass
    """
    def _inner_require_optional(func):
        import importlib
        @wraps(func)
        def wrapper(*args, **kwargs):
            missing_module = False
            for mod in module_list:
                try:
                    func.__globals__[mod] = importlib.import_module(mod)
                except ImportError:
                    print("Error: This func requires module \"{}\" to run.".format(mod))
                    missing_module = True
            if not missing_module:
                return func(*args, **kwargs)
        return wrapper
    return _inner_require_optional


@require_optional("graphviz")
def visualize(edges, size=None):
    if size:
        d = graphviz.Digraph(graph_attr=[('size', size)])    # pylint: disable=undefined-variable
    else:
        d = graphviz.Digraph()                               # pylint: disable=undefined-variable
    for _item in edges:
        d.edge(_item[0], _item[1])
    return d
