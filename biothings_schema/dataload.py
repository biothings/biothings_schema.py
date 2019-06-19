import json

import requests
import yaml
import networkx as nx

from .utils import dict2list

SCHEMAORG_PATH = 'https://api.github.com/repos/schemaorg/schemaorg/contents/data/releases'

DATATYPES = ["http://schema.org/DataType", "http://schema.org/Boolean",
             "http://schema.org/False", "http://schema.org/True",
             "http://schema.org/Date", "http://schema.org/DateTime",
             "http://schema.org/Number", "http://schema.org/Integer",
             "http://schema.org/Float", "http://schema.org/Text",
             "http://schema.org/CssSelectorType", "http://schema.org/URL",
             "http://schema.org/XPathType", "http://schema.org/Time"]


def load_json_or_yaml(file_path):
    """Load either json or yaml document from file path or url or JSON doc

    :arg str file_path: The path of the url doc, could be url or file path
    """
    # handle json doc
    if isinstance(file_path, dict):
        return file_path
    # handle url
    elif file_path.startswith("http"):
        with requests.get(file_path) as url:
            # check if http requests returns a success status code
            if url.status_code != 200:
                raise ValueError("Invalid URL!")
            else:
                _data = url.content
    # handle file path
    else:
        try:
            with open(file_path) as f:
                _data = f.read()
        except FileNotFoundError:
            raise ValueError("Invalid File Path!")
    try:
        data = json.loads(_data)
    except json.JSONDecodeError:   # for py>=3.5
    # except ValueError:               # for py<3.5
        try:
            data = yaml.load(_data, Loader=yaml.SafeLoader)
        except (yaml.scanner.ScannerError,
                yaml.parser.ParserError):
            raise ValueError("Not a valid JSON or YAML format.")
    return data


def normalize_rdfs_label_field(schema):
    """schemaorg file has some discrepancy, fix them"""
    graph = []
    for _record in schema["@graph"]:
        if "http://schema.org/supersededBy" not in _record:
            if "rdfs:label" in _record and type(_record["rdfs:label"]) == dict:
                _record["rdfs:label"] = _record["rdfs:label"]["@value"]
            graph.append(_record)
    schema["@graph"] = graph
    return schema


def get_latest_schemaorg_version():
    """Get the latest version of schemaorg from its github"""
    response = load_json_or_yaml(SCHEMAORG_PATH)
    versions = [float(_item['name']) for _item in response if 'name' in _item]
    versions.sort()
    return str(versions[-1])


def construct_schemaorg_url(version):
    """Construct url to schemaorg jsonld file"""
    return "https://raw.githubusercontent.com/schemaorg/schemaorg/master/data/releases/" + str(version) + "/all-layers.jsonld"


def load_schemaorg(version=None, verbose=False):
    """Load SchemOrg vocabulary

    :arg float version: The schemaorg schema version, e.g 3.7
    """
    # if version is not specified, use the latest one by default
    if not version:
        version = get_latest_schemaorg_version()
    url = construct_schemaorg_url(version)
    if verbose:
        print("Loading Schema.org schema from {}".format(url))
    try:
        return load_json_or_yaml(url)
    except ValueError:
        raise ValueError("version {} is not valid! Current latest version is {}".format(version, get_latest_schemaorg_version()))


def load_schema_class_into_networkx(schema, preload_schemaorg=False):
    """Constuct networkx DiGraph based on Schema provided"""
    # preload all schema from schemaorg latest version
    if preload_schemaorg:
        G = load_schema_class_into_networkx(preload_schemaorg,
                                            preload_schemaorg=False)
    else:
        G = nx.DiGraph()
    for record in schema["@graph"]:
        if record["@type"] == "rdfs:Class" and record["@id"] not in DATATYPES:
            G.add_node(record["@id"],
                       uri=record["@id"],
                       description=record["rdfs:comment"])
            if "rdfs:subClassOf" in record:
                parents = record["rdfs:subClassOf"]
                if isinstance(parents, list):
                    for _parent in parents:
                        G.add_edge(_parent["@id"],
                                   record["@id"])
                elif isinstance(parents, dict):
                    G.add_edge(parents["@id"],
                               record["@id"])
                else:
                    raise ValueError('"dictionary" input is not a list or dict')
            else:
                pass
    return G


def load_schema_property_into_networkx(schema, preload_schemaorg=False):
    """Constuct networkx DiGraph based on Schema provided"""
    # preload all schema from schemaorg latest version
    if preload_schemaorg:
        G = load_schema_property_into_networkx(preload_schemaorg,
                                               preload_schemaorg=False)
    else:
        G = nx.DiGraph()
    for record in schema["@graph"]:
        if record["@type"] == "rdf:Property":
            G.add_node(record["@id"],
                       uri=record["@id"],
                       description=record["rdfs:comment"])
            if "rdfs:subPropertyOf" in record:
                parents = record["rdfs:subPropertyOf"]
                if isinstance(parents, list):
                    for _parent in parents:
                        G.add_edge(_parent["@id"],
                                   record["@id"])
                elif isinstance(parents, dict):
                    G.add_edge(parents["@id"],
                               record["@id"])
                else:
                    raise ValueError('"dictionary" input is not a list or dict')
            else:
                pass
    return G


def load_schema_datatype_into_networkx(schema):
    """Construct networkx DiGraph for data types based on Schema provided"""

    G = nx.DiGraph()
    for record in schema["@graph"]:
        if record["@id"] in DATATYPES:
            G.add_node(record["@id"],
                       uri=record["@id"],
                       description=record["rdfs:comment"])
            if "rdfs:subClassOf" in record:
                parents = dict2list(record["rdfs:subClassOf"])
                for _parent in parents:
                    if _parent["@id"] != "rdfs:Class":
                        G.add_edge(_parent["@id"],
                                   record["@id"])
            elif "@type" in record and "http://schema.org/DataType" in record["@type"]:
                G.add_edge("http://schema.org/DataType", record["@id"])
    return G


def get_clean_schema_context(schema):
    """return the clean prefix list from "@content" for only those are used"""
    _schema = load_json_or_yaml(schema)
    context = _schema.get('@context', [])
    if context:
        graph = _schema.get('@graph', [])
        graph = json.dumps(graph)
        used_prefix_li = []
        for prefix in context:
            if graph.find(prefix + ":") != -1:
                used_prefix_li.append(prefix)
        clean_context = {
            "@context": {prefix: context[prefix] for prefix in sorted(set(used_prefix_li))}
        }
        return clean_context
    else:
        print('No "@context" found in the schema')
