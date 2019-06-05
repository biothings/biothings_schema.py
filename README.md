biothings_schema
==========================

biothings_schema is a Python Package to help you view, analyze and edit schemas defined in [schema.org](http://schema.org) way

``` {.sourceCode .python}
>>> from biothings_schema import Schema
>>> se = Schema()
>>> schema_file_path = "https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld"
>>> se.load_schema(schema_file_path)
>>> se.find_parent_classes('Gene')
[   [   'Thing',
        'BiologicalEntity',
        'MolecularEntity',
        'GenomicEntity',
        'MacromolecularMachine',
        'GeneOrGeneProduct']]
>>> se.find_class_specific_properties('Gene')
[   'hgnc',
    'mgi',
    'rgd',
    'rgd',
    'flybase',
    'sgd',
    'pombase',
    'dictybase',
    'tair',
    'inTaxon',
    'entrez',
    'pharos',
    'pharmgkb',
    'symbol',
    'omim',
    'umls',
    'unigene',
    'geneticallyInteractsWith',
    'hasGeneProduct',
    'hasTranscript',
    'geneAssociatedWithCondition']
```

See [detailed jupyter notebook demo](https://github.com/biothings/biothings_schema.py/tree/master/jupyter%20notebooks).


Feature Support
---------------


Installation
------------

To install biothings_schema, simply use pip:

``` {.sourceCode .bash}
$ pip install git+https://github.com/biothings/biothings_schema.py#egg=biothings_schema.py
```

Documentation
-------------

Fantastic documentation is available at <>.

How to Contribute
-----------------

