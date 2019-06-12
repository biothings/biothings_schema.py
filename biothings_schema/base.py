import json
import os
from functools import wraps
from jsonschema import validate

from .dataload import load_json_or_yaml

_ROOT = os.path.abspath(os.path.dirname(__file__))


def validate_schema(schema):
    """Validate schema against SchemaORG standard"""
    json_schema_path = os.path.join(_ROOT, 'data', 'schema.json')
    json_schema = load_json_or_yaml(json_schema_path)
    return validate(schema, json_schema)


def validate_property_schema(schema):
    """Validate schema against SchemaORG property definition standard"""
    json_schema_path = os.path.join(_ROOT, 'data', 'property_json_schema.json')
    json_schema = load_json_or_yaml(json_schema_path)
    return validate(schema, json_schema)


def validate_class_schema(schema):
    """Validate schema against SchemaORG class definition standard"""
    json_schema_path = os.path.join(_ROOT, 'data', 'class_json_schema.json')
    json_schema = load_json_or_yaml(json_schema_path)
    return validate(schema, json_schema)


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
