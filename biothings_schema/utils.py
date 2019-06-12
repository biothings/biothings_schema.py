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
    """
    return set([x for x in _list if _list.count(x) > 1])


def dict2list(dictionary):
    if isinstance(dictionary, list):
        return dictionary
    elif isinstance(dictionary, dict):
        return [dictionary]
    else:
        raise ValueError('"dictionary" input is not a list or dict')


def str2list(_str):
    if isinstance(_str, str):
        return [_str]
    elif isinstance(_str, list):
        return _str
    else:
        raise ValueError('"_str" input is not a str or list')


def unlist(_list):
    """ if list is of length 1, return only the first item
    """
    if len(_list) == 1:
        return _list[0]
    else:
        return _list
