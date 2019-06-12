biothings_schema
==========================

[![image](https://raw.githubusercontent.com/biothings/biothings_schema.py/master/docs/images/descendant_classes.png)](https://github.com/biothings/biothings_schema.py)

biothings_schema is a Python Package to help you view, analyze and edit schemas defined in [schema.org](http://schema.org) way

``` {.sourceCode .python}
>>> from biothings_schema import Schema
>>> se = Schema()
>>> schema_file_path = "https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld"
>>> se.load_schema(schema_file_path)
>>> scls = se.get_class("Gene")
>>> scls.parent_classes
[[<SchemaClass "Thing">,
  <SchemaClass "BiologicalEntity">,
  <SchemaClass "MolecularEntity">,
  <SchemaClass "GenomicEntity">,
  <SchemaClass "MacromolecularMachine">,
  <SchemaClass "GeneOrGeneProduct">]]
>>> scls.list_properties(group_by_class=False)
[<SchemaProperty "mgi"">,
 <SchemaProperty "pombase"">,
 <SchemaProperty "rgd"">,
 <SchemaProperty "umls"">,
 <SchemaProperty "omim"">,
 <SchemaProperty "hasTranscript"">,
 <SchemaProperty "dictybase"">,
 <SchemaProperty "geneAssociatedWithCondition"">,
 <SchemaProperty "flybase"">,
 <SchemaProperty "hasGeneProduct"">,
 <SchemaProperty "pharos"">,
 <SchemaProperty "pharmgkb"">,
 <SchemaProperty "unigene"">,
 <SchemaProperty "symbol"">,
 <SchemaProperty "zfin"">,
 <SchemaProperty "entrez"">,
 <SchemaProperty "inTaxon"">,
 <SchemaProperty "hgnc"">,
 <SchemaProperty "geneticallyInteractsWith"">,
 <SchemaProperty "tair"">,
 <SchemaProperty "sgd"">]
```

See [detailed jupyter notebook demo](https://github.com/biothings/biothings_schema.py/tree/master/jupyter%20notebooks).


Feature Support
---------------
1. [Visulize schema structure](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Visualizing%20Schema.ipynb)
2. [Find ancestors/descendants of a schema class](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Explore%20classes%20and%20properties%20of%20Schema.ipynb)
3. [Find properties associated with a schema class](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Explore%20classes%20and%20properties%20of%20Schema.ipynb)
4. [Validate your schema against JSON schema](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Validate%20JSON%20using%20json%20schema%20defined%20in%20Schema%20file.ipynb)
5. Edit/Extend your schema

Installation
------------

To install biothings_schema, simply use pip:

``` {.sourceCode .bash}
$ pip install git+https://github.com/biothings/biothings_schema.py#egg=biothings_schema.py
```

Documentation
-------------

Fantastic documentation is available at <Coming soon!>.

How to Contribute
-----------------
<Coming soon!>
