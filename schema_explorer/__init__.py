from .base import *
import networkx as nx
import tabletext


class SchemaExplorer():
    """Class for exploring schema
    """
    def __init__(self):
        self.load_default_schema()
        print('Preloaded with BioLink schema. Upload your own schema using "load_schema" function.')

    def expand_curies_in_schema(self):
        context = self.schema["@context"]
        graph = self.schema["@graph"]
        new_schema = {"@context": context,
                      "@graph": [],
                      "@id": self.schema["@id"]}
        for record in graph:
            new_record = {}
            for k, v in record.items():
                if type(v) == str:
                    new_record[expand_curie_to_uri(k, context)] =  expand_curie_to_uri(v, context)
                elif type(v) == list:
                    if type(v[0]) == dict:
                        new_record[expand_curie_to_uri(k, context)] = []
                        for _item in v:
                            new_record[expand_curie_to_uri(k, context)].append({"@id": expand_curie_to_uri(_item["@id"], context)})
                    else:
                        new_record[expand_curie_to_uri(k, context)] = [expand_curie_to_uri(_item, context) for _item in v]
                elif type(v) == dict and "@id" in v:
                    new_record[expand_curie_to_uri(k, context)] = {"@id": expand_curie_to_uri(v["@id"], context)}
            new_schema["@graph"].append(new_record)
        return new_schema

    def curie2uri(self, curie):
        prefix, value = curie.split(':')
        uri = self.schema["@context"][prefix] + value
        return uri

    def uri2label(self, uri):
        """Given a URI, return the label
        """
        return [record["rdfs:label"] for record in self.schema["@graph"] if record['@id'] == uri][0]

    def load_schema(self, schema):
        """Load schema and convert it to networkx graph
        """
        self.schema = load_json(schema)
        validate_schema(self.schema)
        self.schema_nx = load_schema_into_networkx(self.schema)

    def load_default_schema(self):
        """Load default schema, either schema.org or biothings
        """
        self.schema = load_default()
        self.schema_nx = load_schema_into_networkx(self.schema)

    def full_schema_graph(self, size=None):
        edges = self.schema_nx.edges()
        return visualize(edges, size=size)

    def sub_schema_graph(self, source, direction, size=None):
        if direction == 'down':
            edges = list(nx.edge_bfs(self.schema_nx, [source]))
            return visualize(edges, size=size)
        elif direction == 'up':
            paths = self.find_parent_classes(source)
            edges = []
            for _path in paths:
                _path.append(source)
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
            return visualize(edges, size=size)
        elif direction == "both":
            paths = self.find_parent_classes(source)
            edges = list(nx.edge_bfs(self.schema_nx, [source]))
            for _path in paths:
                _path.append(source)
                for i in range(0, len(_path) - 1):
                    edges.append((_path[i], _path[i + 1]))
            return visualize(edges, size=size)

    def find_parent_classes(self, schema_class):
        """Find all parents of the class
        """
        root_node = list(nx.topological_sort(self.schema_nx))[0]
        paths = nx.all_simple_paths(self.schema_nx,
                                    source=root_node,
                                    target=schema_class)
        return [_path[:-1] for _path in paths]

    def find_class_specific_properties(self, schema_class):
        """Find properties specifically associated with a given class
        """
        schema_uri = self.schema_nx.node[schema_class]["uri"]
        properties = []
        for record in self.schema["@graph"]:
            if record['@type'] == "rdf:Property":
                if type(record["schema:domainIncludes"]) == dict and record["schema:domainIncludes"]["@id"] == schema_uri:
                    properties.append(record["rdfs:label"])
                elif type(record["schema:domainIncludes"]) == list and [item for item in record["schema:domainIncludes"] if item["@id"] == schema_uri] != []:
                    properties.append(record["rdfs:label"])
        return properties

    def find_all_class_properties(self, schema_class, display_as_table=False):
        """Find all properties associated with a given class
        # TODO : need to deal with recursive paths
        """
        parents = self.find_parent_classes(schema_class)
        properties = [{'class': schema_class,
                       'properties': self.find_class_specific_properties(schema_class)}]
        for path in parents:
            path.reverse()
            for _parent in path:
                properties.append({"class": _parent,
                                    "properties": self.find_class_specific_properties(_parent)})
        if not display_as_table:
            return properties
        else:
            content = [['Property', 'Expected Type', 'Description', 'Class']]
            for record in properties:
                for _property in record['properties']:
                    property_info = self.explore_property(_property)
                    content.append([_property, property_info['range'],
                                    property_info['description'],
                                    record['class']])
            print(tabletext.to_text(content))

    def find_class_usages(self, schema_class):
        """Find where a given class is used as a value of a property
        """
        usages = []
        schema_uri = self.schema_nx.node[schema_class]["uri"]
        for record in self.schema["@graph"]:
            usage = {}
            if record["@type"] == "rdf:Property":
                p_range = dict2list(record["schema:rangeIncludes"])
                for _doc in p_range:
                    if _doc['@id'] == schema_uri:
                        usage["property"] = record["rdfs:label"]
                        p_domain = dict2list(record["schema:domainIncludes"])
                        usage["property_used_on_class"] = unlist([self.uri2label(record["@id"]) for record in p_domain])
                        usage["description"] = record["rdfs:comment"]
            if usage:
                usages.append(usage)
        return usages

    def find_child_classes(self, schema_class):
        """Find schema classes that inherit from the given class
        """
        return unlist(list(self.schema_nx.successors(schema_class)))

    def explore_class(self, schema_class):
        """Find details about a specific schema class
        """
        class_info = {'properties': self.find_all_class_properties(schema_class),
                      'description': self.schema_nx.node[schema_class]['description'],
                      'uri': self.curie2uri(self.schema_nx.node[schema_class]["uri"]),
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
                    property_info["uri"] = self.curie2uri(record["@id"])
                    p_domain = dict2list(record["schema:domainIncludes"])
                    property_info["domain"] = unlist([self.uri2label(record["@id"]) for record in p_domain])
                    p_range = dict2list(record["schema:rangeIncludes"])
                    property_info["range"] = unlist([self.uri2label(record["@id"]) for record in p_range])
        return property_info

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
        self.schema_nx = load_schema_into_networkx(self.schema)

    def update_property(self, property_info):
        """Add a new property into schema
        """
        validate_property_schema(property_info)
        self.schema["@graph"].append(property_info)
        validate_schema(self.schema)
        print("Updated the property {} successfully!".format(property_info["rdfs:label"]))

    def export_schema(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.schema, f, sort_keys = True, indent = 4,
               ensure_ascii = False)
