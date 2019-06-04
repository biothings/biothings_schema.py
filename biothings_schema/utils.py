
def expand_curie_to_uri(curie, context_info):
    """Expand curie to uri based on the context given

    parmas
    ======
    curie: curie to be expanded (e.g. bts:BiologicalEntity)
    context_info: jsonld context specifying prefix-uri relation (e.g. {"bts":
    "http://schema.biothings.io/"})
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


def expand_curies_in_schema(schema):
    """Expand all curies in a SchemaOrg JSON-LD file into URI
    """
    context = schema["@context"]
    graph = schema["@graph"]
    new_schema = {"@context": context,
                  "@graph": []}
    for record in graph:
        new_record = {}
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
        new_schema["@graph"].append(new_record)
    return new_schema


def merge_schema(schema1, schema2):
    """Merge two schemas together"""
    new_schema = {"@context": {},
                  "@graph": [],
                  "@id": "merged"}
    new_schema["@context"] = schema1["@context"]
    new_schema["@context"].update(schema2["@context"])
    new_schema["@graph"] = schema1["@graph"] + schema2["@graph"]
    return new_schema


def uri2label(uri, schema=None):
    """Given a URI, return the label
    """
    # if schema is provided, look into the schema for the label
    if schema:
        return [record["rdfs:label"] for record in schema["@graph"] if record['@id'] == uri][0]
    # otherwise, extract the last element after "/"
    elif '/' in uri:
        return uri.split('/')[-1]
    elif ':' in uri:
        return uri.split(':')[-1]
    else:
        return uri


def find_duplicates(_list):
    """Find duplicate items in a list
    """
    return set([x for x in _list if _list.count(x) > 1])
