import json
from functools import lru_cache, wraps
try:
    from time import monotonic_ns     # For Python >=3.7
except ImportError:
    from time import monotonic
    monotonic_ns = lambda: monotonic() * 10 ** 9     # noqa

import networkx as nx


def merge_schema(*schema_list):
    """Merge a list of schemas together"""
    new_schema = {"@context": {},
                  "@graph": [],
                  "@id": "merged"}
    _ids = ["merged"]
    for schema in schema_list:
        new_schema["@context"].update(schema.get("@context", {}))
        new_schema["@graph"].extend(schema.get("@graph", []))
        _id = schema.get('@id', None)
        if _id:
            _ids.append(_id)
    new_schema["@id"] = "_".join(_ids)
    return new_schema


def merge_schema_networkx(g1, g2):
    """
    Merge two networkx DiGraphs
    For duplicated nodes/edges, the attributes from g2 take precedent over g1.
    """
    return nx.compose(g1, g2)


def find_duplicates_0(_list):
    """ deprecated.
    Find duplicate items in a list

    :arg list _list: a python list
    """
    return set([x for x in _list if _list.count(x) > 1])


def find_duplicates(_list):
    """a more efficient way to return duplicated items
    ref: https://www.iditect.com/guide/python/python_howto_find_the_duplicates_in_a_list.html

    :arg list _list: a python list
    """
    first_seen = set()
    first_seen_add = first_seen.add
    duplicates = set(i for i in _list if i in first_seen or first_seen_add(i))
    # turn the set into a list (as requested)
    return duplicates


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


# From: https://gist.github.com/Morreski/c1d08a3afa4040815eafd3891e16b945?permalink_comment_id=3521580#gistcomment-3521580
def timed_lru_cache(
    _func=None, *, seconds: int = 600, maxsize: int = 128, typed: bool = False
):
    """Extension of functools lru_cache with a timeout

    Parameters:
    seconds (int): Timeout in seconds to clear the WHOLE cache, default = 10 minutes
    maxsize (int): Maximum Size of the Cache
    typed (bool): Same value of different type will be a different entry

    """

    def wrapper_cache(f):
        f = lru_cache(maxsize=maxsize, typed=typed)(f)
        f.delta = seconds * 10 ** 9
        f.expiration = monotonic_ns() + f.delta

        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if monotonic_ns() >= f.expiration:
                f.cache_clear()
                f.expiration = monotonic_ns() + f.delta
            return f(*args, **kwargs)

        wrapped_f.cache_info = f.cache_info
        wrapped_f.cache_clear = f.cache_clear
        return wrapped_f

    # To allow decorator to be used without arguments
    if _func is None:
        return wrapper_cache
    else:
        return wrapper_cache(_func)
