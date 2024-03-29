[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a181e07380c2450eab1e26837f0322de)](https://www.codacy.com/gh/biothings/biothings_schema.py/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=biothings/biothings_schema.py&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/a181e07380c2450eab1e26837f0322de)](https://www.codacy.com/gh/biothings/biothings_schema.py/dashboard?utm_source=github.com&utm_medium=referral&utm_content=biothings/biothings_schema.py&utm_campaign=Badge_Coverage)

biothings_schema
==========================

[![image](https://raw.githubusercontent.com/biothings/biothings_schema.py/master/docs/images/descendant_classes.png)](https://github.com/biothings/biothings_schema.py)

biothings_schema is a Python package for the creation, extension and exploration of the schemas defined using the [schema.org](http://schema.org) standard.


Feature Support
---------------
1. [Visulize schema structure](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Visualizing%20Schema.ipynb)
[![image](https://raw.githubusercontent.com/biothings/biothings_schema.py/master/docs/images/all_classes.png)](https://github.com/biothings/biothings_schema.py)
2. [Find ancestors/descendants of a schema class](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Explore%20classes%20and%20properties%20of%20Schema.ipynb)

``` {.sourceCode .python}
In [1]: from biothings_schema import Schema

In [2]: schema_file_path = "https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld"

In [3]: se = Schema(schema_file_path)

In [4]: scls = se.get_class("Gene")

In [5]: scls.parent_classes

Out [5]:
[[<SchemaClass "Thing">,
  <SchemaClass "BiologicalEntity">,
  <SchemaClass "MolecularEntity">,
  <SchemaClass "GenomicEntity">,
  <SchemaClass "MacromolecularMachine">,
  <SchemaClass "GeneOrGeneProduct">]]

In [6]: scls = se.get_class("MolecularEntity")

In [7]: scls.descendant_classes

Out [7]:
[<SchemaClass "Genome">,
 <SchemaClass "RnaProductIsoform">,
 <SchemaClass "GeneProduct">,
 <SchemaClass "Metabolite">,
 <SchemaClass "Protein">,
 <SchemaClass "MacromolecularComplex">,
 <SchemaClass "Microrna">,
 <SchemaClass "Exon">,
 <SchemaClass "RnaProduct">,
 <SchemaClass "CodingSequence">,
 <SchemaClass "GeneProductIsoform">,
 <SchemaClass "GeneFamily">,
 <SchemaClass "Drug">,
 <SchemaClass "Haplotype">,
 <SchemaClass "ChemicalSubstance">,
 <SchemaClass "Genotype">,
 <SchemaClass "ProteinIsoform">,
 <SchemaClass "NoncodingRnaProduct">,
 <SchemaClass "GeneOrGeneProduct">,
 <SchemaClass "Gene">,
 <SchemaClass "MacromolecularMachine">,
 <SchemaClass "Transcript">,
 <SchemaClass "SequenceVariant">,
 <SchemaClass "GenomicEntity">]
```
3. [Find properties associated with a schema class](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Explore%20classes%20and%20properties%20of%20Schema.ipynb)

``` {.sourceCode .python}
In [8]: scls = se.get_class("Gene")

In [9]: scls.list_properties(group_by_class=False)

Out [9]:
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

4. [Validate your schema against JSON schema](https://github.com/biothings/biothings_schema.py/blob/master/jupyter%20notebooks/Validate%20JSON%20using%20json%20schema%20defined%20in%20Schema%20file.ipynb)

5. Edit/Extend your schema


For all features supported by biothings_schema as well as their usage, please see [detailed jupyter notebook demo](https://github.com/biothings/biothings_schema.py/tree/master/jupyter%20notebooks).

Installation
------------

To install biothings_schema, simply use pip:

``` {.sourceCode .bash}
$ pip install git+https://github.com/biothings/biothings_schema.py#egg=biothings_schema
```

Documentation
-------------

Fantastic documentation is available at <https://biothings-schemapy.readthedocs.io/en/latest/>.

The Contributor Guide
---------------------
If you want to contribute to the project, please refer to the contribution guidelines [here](https://github.com/biothings/biothings_schema.py/blob/master/CONTRIBUTING.md)
