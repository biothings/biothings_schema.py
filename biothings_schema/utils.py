import json


def merge_schema(schema1, schema2):
    """Merge two schemas together"""
    new_schema = {"@context": {},
                  "@graph": [],
                  "@id": "merged"}
    new_schema["@context"] = schema1["@context"]
    new_schema["@context"].update(schema2["@context"])
    new_schema["@graph"] = schema1["@graph"] + schema2["@graph"]
    return new_schema


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
