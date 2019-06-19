import re
from collections import defaultdict

from .utils import unlist


class CurieUriConverter():
    """Converte between Curies, URIs and names"""

    def __init__(self, context, uri_list=[]):
        self.context = context
        self.uri_list = uri_list
        # map URI to its corresponding names
        self.name_dict = defaultdict(list)
        for _uri in self.uri_list:
            _name = self.get_label(_uri)
            self.name_dict[_name].append(_uri)

    def determine_id_type(self, _id):
        """Determine whether an ID is a curie or URI or none of them"""
        regex_url = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex_url, _id):
            return 'url'
        elif len(_id.split(":")) == 2 and type(_id.split(":")[0]) == str:
            return 'curie'
        else:
            return 'name'

    def get_uri(self, _input):
        """Convert input to URI format"""
        # first determine the type of input, e.g. URI, CURIE, or Name
        _type = self.determine_id_type(_input)
        # if input type is URL, return itself
        if _type == "url":
            return _input
        # if input type is curie, try convert to URI, if not, return curie
        elif _type == "curie":
            prefix, suffix = _input.split(':')
            if prefix in self.context:
                namespace_url = self.context[prefix]
                if not namespace_url.endswith('/'):
                    namespace_url += '/'
                return namespace_url + suffix
            else:
                return _input
        # if input type is name, try convert to URI, if not, return name
        else:
            if _input in self.name_dict:
                return unlist(self.name_dict[_input])
            else:
                return _input

    def get_curie(self, _input):
        """Convert input to CURIE format"""
        # first determine the type of input, e.g. URI, CURIE, or Name
        _type = self.determine_id_type(_input)
        # if input type is CURIE, return itself
        if _type == "curie":
            return _input
        # if input type is URI, try convert to CUIRE, if not, return URI
        elif _type == "url":
            uri, name = _input.rsplit('/', 1)
            uri += '/'
            prefix = None
            for k, v in self.context.items():
                if v == uri:
                    prefix = k
            if prefix:
                return prefix + ':' + name
            else:
                return _input
        else:
            if _input in self.name_dict:
                uris = self.name_dict[_input]
                curies = []
                for _uri in uris:
                    curies.append(self.get_curie(_uri))
                return unlist(curies)
            else:
                return _input

    def get_prefix(self, _input):
        """Get prefix from input"""
        # first determine the type of input, e.g. URI, CURIE, or Name
        _type = self.determine_id_type(_input)
        # if input type is CURIE, return itself
        if _type == "curie":
            return _input.split(':')[0]
        # if input type is URI, try convert to CUIRE, if not, return URI
        elif _type == "url":
            uri, name = _input.rsplit('/', 1)
            uri += '/'
            prefix = None
            for k, v in self.context.items():
                if v == uri:
                    prefix = k
            if prefix:
                return prefix
            else:
                return None
        else:
            if _input in self.name_dict:
                uris = self.name_dict[_input]
                prefixes = []
                for _uri in uris:
                    prefixes.append(self.get_prefix(_uri))
                return unlist(prefixes)
            else:
                return None

    def get_label(self, _input):
        """Convert input to CURIE format
        TODO: URL could contain #
        """
        # first determine the type of input, e.g. URI, CURIE, or Name
        _type = self.determine_id_type(_input)
        if _type == 'name':
            return _input
        elif _type == 'url':
            return _input.split('/')[-1]
        else:
            return _input.split(':')[-1]


def expand_curie_to_uri(curie, context_info):
    """Expand curie to uri based on the context given

    :arg str curie: curie to be expanded (e.g. bts:BiologicalEntity)
    :arg dict context_info: jsonld context specifying prefix-uri relation (e.g. {"bts": "http://schema.biothings.io/"})
    """
    # as suggested in SchemaOrg standard file, these prefixes don't expand
    PREFIXES_NOT_EXPAND = ["rdf", "rdfs", "xsd"]
    # determine if a value is curie
    if len(curie.split(':')) == 2:
        prefix, value = curie.split(":")
        if prefix in context_info and prefix not in PREFIXES_NOT_EXPAND:
            return context_info[prefix] + value
    # if the input is not curie, return the input unmodified
        else:
            return curie
    else:
        return curie


def preprocess_schema(schema):
    """Expand all curies in a SchemaOrg JSON-LD file into URI

    :arg dict schema: A JSON-LD object representing the schema
    """
    context = schema["@context"]
    new_schema = {"@context": context,
                  "@graph": []}
    for record in schema["@graph"]:
        # if a class is superseded, no need to load into graph
        if "http://schema.org/supersededBy" not in record:
            new_record = {}
            # convert rdfs:label to str if its a dict
            if isinstance(record["rdfs:label"], dict):
                record["rdfs:label"] = record["rdfs:label"]["@value"]
            for k, v in record.items():
                if k == "$validation":
                    new_record[k] = v
                elif isinstance(v, str):
                    new_record[expand_curie_to_uri(k, context)] = expand_curie_to_uri(v, context)
                elif isinstance(v, list):
                    if isinstance(v[0], dict):
                        new_record[expand_curie_to_uri(k, context)] = []
                        for _item in v:
                            new_record[expand_curie_to_uri(k, context)].append({"@id": expand_curie_to_uri(_item["@id"], context)})
                    else:
                        new_record[expand_curie_to_uri(k, context)] = [expand_curie_to_uri(_item, context) for _item in v]
                elif isinstance(v, dict) and "@id" in v:
                    new_record[expand_curie_to_uri(k, context)] = {"@id": expand_curie_to_uri(v["@id"], context)}
                elif v is None:
                    new_record[expand_curie_to_uri(k, context)] = None
                else:
                    new_record[expand_curie_to_uri(k, context)] = v
            new_schema["@graph"].append(new_record)
        else:
            continue
    return new_schema


def extract_name_from_uri_or_curie(item, schema=None):
    """Extract name from uri or curie

    :arg str item: an URI or curie
    :arg dict schema: a JSON-LD representation of schema
    """
    # if schema is provided, look into the schema for the label
    if schema:
        name = [record["rdfs:label"] for record in schema["@graph"] if record['@id'] == item]
        if name:
            return name[0]
        else:
            return extract_name_from_uri_or_curie(item)
    # handle curie, get the last element after ":"
    elif 'http' not in item and len(item.split(":")) == 2:
        return item.split(":")[-1]
    # handle URI, get the last element after "/"
    elif len(item.split("//")[-1].split('/')) > 1:
        return item.split("//")[-1].split('/')[-1]
    # otherwise, rsise ValueError
    else:
        raise ValueError('{} should be converted to either URI or curie'.format(item))
