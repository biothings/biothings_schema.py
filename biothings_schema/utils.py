import json
import networkx as nx


def merge_schema(schema1, schema2):
    """Merge two schemas together"""
    new_schema = {"@context": {},
                  "@graph": [],
                  "@id": "merged"}
    new_schema["@context"] = schema1["@context"]
    new_schema["@context"].update(schema2["@context"])
    new_schema["@graph"] = schema1["@graph"] + schema2["@graph"]
    return new_schema


def merge_schema_networkx(g1, g2):
    """Merge two networkx DiGraphs"""
    return nx.compose(g1, g2)


def find_duplicates(_list):
    """Find duplicate items in a list

    :arg list _list: a python list
    """
    return set([x for x in _list if _list.count(x) > 1])


def dict2list(dictionary):
    """Convert python dict to list of one dictionary

    :arg dict dictionary: a python dictionary
    """
    if isinstance(dictionary, list):
        return dictionary
    elif isinstance(dictionary, dict):
        return [dictionary]
    else:
        raise ValueError('"dictionary" input is not a list or dict')


def str2list(_str):
    """Convert string type to list of one string

    :arg str _str: a string
    """
    if isinstance(_str, str):
        return [_str]
    elif isinstance(_str, list):
        return _str
    else:
        raise ValueError('"_str" input is not a str or list')


def unlist(_list):
    """ if list is of length 1, return only the first item

    :arg list _list: a python list
    """
    if len(_list) == 1:
        return _list[0]
    else:
        return _list


def export_json(json_doc, file_path):
    """Export JSON doc to file"""
    with open(file_path, 'w') as f:
        json.dump(json_doc, f, sort_keys=True,
                  indent=4, ensure_ascii=False)


def expand_ref(json_obj, definition):
    """expand the $ref in json schema"""
    if isinstance(json_obj, dict):
        for key in list(json_obj.keys()):
            if key == "$ref":
                if json_obj[key].startswith("#/definitions/"):
                    concept = json_obj[key].split('/')[-1]
                    if concept in definition:
                        json_obj.pop("$ref")
                        json_obj.update(definition[concept])
                    else:
                        raise ValueError("{} is not defined".format(json_obj[key]))
            elif isinstance(json_obj[key], dict):
                resolved = expand_ref(json_obj[key], definition)
                json_obj[key] = resolved
            elif isinstance(json_obj[key], list):
                for (k, v) in enumerate(json_obj[key]):
                    resolved = expand_ref(v, definition)
                    if resolved:
                        json_obj[key][k] = resolved
    elif isinstance(json_obj, list):
        for (key, value) in enumerate(json_obj):
            resolved = expand_ref(value, definition)
            if resolved:
                json_obj[key] = resolved
    return json_obj
