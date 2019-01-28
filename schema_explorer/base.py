import json
import urllib.request
import os
import networkx as nx
import graphviz
from jsonschema import validate

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
    """
    def __init__(self, schema):
        self.schemaorg = {'schema': load_schemaorg(),
                          'classes': [],
                          'properties': []}
        for _schema in self.schemaorg['schema']['@graph']:
            for _record in _schema["@graph"]:
                _type = dict2list(_record["@type"])
                if "rdf:Property" in _type:
                    self.schemaorg['properties'].append(_record["@id"])
                elif "rdf:Class" in _type:
                    self.schemaorg['classes'].append(_record["@id"])
        self.extension_schema = {'schema': schema}
        for _record in schema["@graph"]:
            _type = dict2list(_record["@type"])
            if "rdf:Property" in _type:
                self.extension_schema['properties'].append(_record["@id"])
            elif "rdf:Class" in _type:
                self.extension_schema['classes'].append(_record["@id"])
        self.all_classes = self.schemaorg['classes'] + self.extension_schema['classes']

    def validate_class_label(self, label_uri):
        label = extract_name_from_uri_or_curie(label_uri)
        assert label[0].isupper()

    def validate_property_label(self, label_uri):
        label = extract_name_from_uri_or_curie(label_uri)
        assert label[0].islower()

    def validate_subclassof_field(self, subclassof_value):
        subclassof_value = dict2list(subclassof_value)
        for record in subclassof_value:
            assert record["@id"] in self.all_classes

    def validate_domainIncludes_field(self, domainincludes_value):
        domainincludes_value = dict2list(domainincludes_value)
        for record in domainincludes_value:
            assert record["@id"] in self.all_classes

    def validate_rangeIncludes_field(self, rangeincludes_value):
        rangeincludes_value = dict2list(rangeincludes_value)
        for record in rangeincludes_value:
            assert record["@id"] in self.all_classes

    def check_whether_atid_and_label_match(self, record):
        _id = extract_name_from_uri_or_curie(record["@id"])
        assert _id == record["rdfs:label"]

    def check_duplicate_labels(self):
        labels = [_record['rdfs:label'] for _recod in self.extension_schema['@graph']]
        assert len(labels) == len(set(labels))

    def validate_schema(self, schema):
    """Validate schema against SchemaORG standard
    """
        json_schema_path = os.path.join(_ROOT, 'data', 'schema.json')
        json_schema = load_json(json_schema_path)
        return validate(schema, json_schema)


    def validate_property_schema(self, schema):
        """Validate schema against SchemaORG property definition standard
        """
        json_schema_path = os.path.join(_ROOT, 'data', 'property_json_schema.json')
        json_schema = load_json(json_schema_path)
        return validate(schema, json_schema)


    def validate_class_schema(self, schema):
        """Validate schema against SchemaORG class definition standard
        """
        json_schema_path = os.path.join(_ROOT, 'data', 'class_json_schema.json')
        json_schema = load_json(json_schema_path)
        return validate(schema, json_schema)

    def validate_full_schema(self):
        self.check_duplicate_labels()




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
    if len(item.split(":")) == 2:
        return item.split(":")[-1]
    elif len(item.split("/")) > 1:
        return item.split("/")[-1]
    else:
        print("error")


def load_schema_into_networkx(schema):
    G = nx.DiGraph()
    for record in schema["@graph"]:
        if record["@type"] == "rdfs:Class":
            G.add_node(record['rdfs:label'], uri=record["@id"],
                       description=record["rdfs:comment"])
            if "rdfs:subClassOf" in record:
                parents = record["rdfs:subClassOf"]
                if type(parents) == list:
                    for _parent in parents:
                        G.add_edge(extract_name_from_uri_or_curie(_parent["@id"]),
                                   record["rdfs:label"])
                elif type(parents) == dict:
                    G.add_edge(extract_name_from_uri_or_curie(parents["@id"]),
                               record["rdfs:label"])
    return G


def dict2list(dictionary):
    if type(dictionary) == list:
        return dictionary
    elif type(dictionary) == dict:
        return [dictionary]


def unlist(_list):
    if len(_list) == 1:
        return _list[0]
    else:
        return _list


def visualize(edges, size=None):
    if size:
        d = graphviz.Digraph(graph_attr=[('size', size)])
    else:
        d = graphviz.Digraph()
    for _item in edges:
        d.edge(_item[0], _item[1])
    return d


def expand_curie_to_uri(curie, context_info):
    """Expand curie to uri based on the context given
    """
    PREFIXES_NOT_EXPAND = ["rdf", "rdfs", "xsd"]
    if len(curie.split(':')) == 2:
        prefix, value = curie.split(":")
        if prefix in context_info and prefix not in PREFIXES_NOT_EXPAND:
            return context_info[prefix] + value
        else:
            return curie
    else:
        return curie
