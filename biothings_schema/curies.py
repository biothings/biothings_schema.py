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


def expand_curies_in_schema(schema):
    """Expand all curies in a SchemaOrg JSON-LD file into URI

    :arg dict schema: A JSON-LD object representing the schema
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


def extract_name_from_uri_or_curie(item, schema=None):
    """Extract name from uri or curie

    :arg str item: an URI or curie
    :arg dict schema: a JSON-LD representation of schema
    """
    # if schema is provided, look into the schema for the label
    if schema:
        return [record["rdfs:label"] for record in schema["@graph"] if record['@id'] == item][0]
    # handle curie, get the last element after ":"
    elif 'http' not in item and len(item.split(":")) == 2:
        return item.split(":")[-1]
    # handle URI, get the last element after "/"
    elif len(item.split("//")[-1].split('/')) > 1:
        return item.split("//")[-1].split('/')[-1]
    # otherwise, rsise ValueError
    else:
        raise ValueError('{} should be converted to either URI or curie'.format(item))
