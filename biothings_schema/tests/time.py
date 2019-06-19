import time

from biothings_schema import Schema


def timeit():
    start = time.time()
    PATH = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'
    se = Schema(PATH)
    clses = se.list_all_classes()
    for _cls in clses:
        es_class = {'schema': None, 'name': None, 'clses': None, 'props': []}
        es_class['schema'] = _cls.prefix
        es_class['name'] = _cls.label
        es_class['clses'] = [', '.join(map(str, schemas))
                             for schemas in _cls.parent_classes]
        for prop in _cls.list_properties(group_by_class=False):
            info = prop.describe()
            _property = {'name': str(prop),
                         'value_types': [str(_type) for _type in info['range']],
                         'description': info.get('description')}

            es_class['props'].append(_property)
    end = time.time()
    print(end - start)


if __name__ == '__main__':
    timeit()
