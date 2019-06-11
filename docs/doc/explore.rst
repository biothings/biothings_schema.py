.. How to explore Schema classes and properties

Explore Classes and Properties Defined in Schema
************************************************

biothings_schema pyton package allows you to explore the classes (e.g. ancestors, descendants, associated properties, etc.) as well as the properties defined within the schema.

.. _list_all_classes:

List all classes defined in schema
-----------------------------------

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: se.list_all_classes()

    Out [4]: [SchemaClass(name=BiologicalEntity),
              SchemaClass(name=Thing),
              SchemaClass(name=OntologyClass),
              SchemaClass(name=RelationshipType),
              SchemaClass(name=GeneOntologyClass),
              ......
              SchemaClass(name=CellLine),
              SchemaClass(name=GrossAnatomicalStructure),
              SchemaClass(name=ProteinStructure)]

.. _find_parent_classes:

Find all parents of a specific class
------------------------------------

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("Gene")

    In [5]: scls.parent_classes

    Out [5]: [[SchemaClass(name=Thing),
               SchemaClass(name=BiologicalEntity),
               SchemaClass(name=MolecularEntity),
               SchemaClass(name=GenomicEntity),
               SchemaClass(name=MacromolecularMachine),
               SchemaClass(name=GeneOrGeneProduct)]]

.. _find_child_classes:

Find all children of a specific class
-------------------------------------

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("MolecularEntity")

    In [5]: scls.child_classes

    Out [5]: [SchemaClass(name=ChemicalSubstance),
              SchemaClass(name=GenomicEntity),
              SchemaClass(name=GeneFamily)]

.. _find_descendant_classes:

Find all descendants of a specific class
----------------------------------------

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("MolecularEntity")

    In [5]: scls.descendant_classes

    Out [5]: [SchemaClass(name=Metabolite),
              SchemaClass(name=ProteinIsoform),
              SchemaClass(name=GeneProduct),
              SchemaClass(name=GeneProductIsoform),
              SchemaClass(name=Genome),
              SchemaClass(name=Haplotype),
              SchemaClass(name=Transcript),
              SchemaClass(name=GeneOrGeneProduct),
              SchemaClass(name=RnaProductIsoform),
              SchemaClass(name=GeneFamily),
              SchemaClass(name=Drug),
              SchemaClass(name=RnaProduct),
              SchemaClass(name=Protein),
              SchemaClass(name=Gene),
              SchemaClass(name=GenomicEntity),
              SchemaClass(name=Microrna),
              SchemaClass(name=CodingSequence),
              SchemaClass(name=MacromolecularMachine),
              SchemaClass(name=Exon),
              SchemaClass(name=SequenceVariant),
              SchemaClass(name=MacromolecularComplex),
              SchemaClass(name=Genotype),
              SchemaClass(name=NoncodingRnaProduct),
              SchemaClass(name=ChemicalSubstance)]

.. _find_associated_properties:

Find properties associated to a specific class
----------------------------------------------

Only fetch properties specifically defined for this class

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("Gene")

    In [5]: scls.list_properties()

    Out [5]: [{'class': 'Gene',
               'properties': [SchemaProperty(name=hgnc),
                              SchemaProperty(name=mgi),
                              SchemaProperty(name=rgd),
                              SchemaProperty(name=zfin),
                              SchemaProperty(name=flybase),
                              SchemaProperty(name=sgd),
                              SchemaProperty(name=pombase),
                              SchemaProperty(name=dictybase),
                              SchemaProperty(name=tair),
                              SchemaProperty(name=inTaxon),
                              SchemaProperty(name=entrez),
                              SchemaProperty(name=pharos),
                              SchemaProperty(name=pharmgkb),
                              SchemaProperty(name=symbol),
                              SchemaProperty(name=omim),
                              SchemaProperty(name=umls),
                              SchemaProperty(name=unigene),
                              SchemaProperty(name=geneticallyInteractsWith),
                              SchemaProperty(name=hasGeneProduct),
                              SchemaProperty(name=hasTranscript),
                              SchemaProperty(name=geneAssociatedWithCondition)]}]

List all properties associated with a class (include properties for its ancestors)

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("Gene")

    In [5]: scls.list_properties(class_specific=False)

    Out [5]: [{'class': 'Gene',
               'properties': SchemaProperty(name=hgnc),
                             SchemaProperty(name=mgi),
                             SchemaProperty(name=rgd),
                             SchemaProperty(name=zfin),
                             SchemaProperty(name=flybase),
                             SchemaProperty(name=sgd),
                             SchemaProperty(name=pombase),
                             SchemaProperty(name=dictybase),
                             SchemaProperty(name=tair),
                             SchemaProperty(name=inTaxon),
                             SchemaProperty(name=entrez),
                             SchemaProperty(name=pharos),
                             SchemaProperty(name=pharmgkb),
                             SchemaProperty(name=symbol),
                             SchemaProperty(name=omim),
                             SchemaProperty(name=umls),
                             SchemaProperty(name=unigene),
                             SchemaProperty(name=geneticallyInteractsWith),
                             SchemaProperty(name=hasGeneProduct),
                             SchemaProperty(name=hasTranscript),
                             SchemaProperty(name=geneAssociatedWithCondition)]}]},
              {'class': 'GeneOrGeneProduct',
               'properties': [SchemaProperty(name=ensembl),
                              SchemaProperty(name=refseq),
                              SchemaProperty(name=metabolize),
                              SchemaProperty(name=targetedBy),
                              SchemaProperty(name=enablesMF),
                              SchemaProperty(name=involvedInBP),
                              SchemaProperty(name=involvedInPathway),
                              SchemaProperty(name=involvedInWikipathway),
                              SchemaProperty(name=involvedInReactomePathway),
                              SchemaProperty(name=hasHomolog),
                              SchemaProperty(name=orthologousTo),
                              SchemaProperty(name=hasProteinStructure),
                              SchemaProperty(name=inPathwayWith),
                              SchemaProperty(name=inComplexWith),
                              SchemaProperty(name=inCellPopulationWith),
                              SchemaProperty(name=expressedIn)]},
              {'class': 'MacromolecularMachine', 'properties': []},
              {'class': 'GenomicEntity', 'properties': []},
              {'class': 'MolecularEntity',
               'properties': [SchemaProperty(name=molecularlyInteractsWith),
                              SchemaProperty(name=affectsAbundanceOf),
                              SchemaProperty(name=increasesAbundanceOf),
                              SchemaProperty(name=decreasesAbundanceOf),
                              SchemaProperty(name=affectsActivityOf),
                              .....
                              SchemaProperty(name=decreasesUptakeOf),
                              SchemaProperty(name=regulates,EntityToEntity),
                              SchemaProperty(name=biomarkerFor)]},
              {'class': 'BiologicalEntity',
               'properties': [SchemaProperty(name=hasPhenotype)]},
              {'class': 'Thing',
               'properties': [SchemaProperty(name=sameAs),
                              SchemaProperty(name=alternateName),
                              SchemaProperty(name=image),
                              SchemaProperty(name=additionalType),
                              SchemaProperty(name=name),
                              SchemaProperty(name=identifier),
                              SchemaProperty(name=subjectOf),
                              SchemaProperty(name=mainEntityOfPage),
                              SchemaProperty(name=url),
                              SchemaProperty(name=potentialAction),
                              SchemaProperty(name=description),
                              SchemaProperty(name=disambiguatingDescription)]}]

.. _find_class_usage:

Find class usage
-------------------

Find where this class has been used in the schema

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("GenomicEntity")

    In [5]: scls.used_by()

    Out [5]: [{'property': SchemaProperty(name=affectsExpressionOf),
               'property_used_on_class': SchemaClass(name=MolecularEntity),
               'description': 'holds between two molecular entities where the action or effect of one changes the level of expression of the other within a system of interest'},
              {'property': SchemaProperty(name=increasesExpressionOf),
               'property_used_on_class': SchemaClass(name=MolecularEntity),
               'description': 'holds between two molecular entities where the action or effect of one increases the level of expression of the other within a system of interest'},
              {'property': SchemaProperty(name=decreasesExpressionOf),
               'property_used_on_class': SchemaClass(name=MolecularEntity),
               'description': 'holds between two molecular entities where the action or effect of one decreases the level of expression of the other within a system of interest'},
              {'property': SchemaProperty(name=affectsMutationRateOf),
               'property_used_on_class': SchemaClass(name=MolecularEntity),
               'description': 'holds between a molecular entity and a genomic entity where the action or effect of the molecular entity impacts the rate of mutation of the genomic entity within a system of interest'},
              {'property': SchemaProperty(name=increasesMutationRateOf),
               'property_used_on_class': SchemaClass(name=MolecularEntity),
               'description': 'holds between a molecular entity and a genomic entity where the action or effect of the molecular entity increases the rate of mutation of the genomic entity within a system of interest'},
              {'property': SchemaProperty(name=decreasesMutationRateOf),
               'property_used_on_class': SchemaClass(name=MolecularEntity),
               'description': 'holds between a molecular entity and a genomic entity where the action or effect of the molecular entity decreases the rate of mutation of the genomic entity within a system of interest'}]


.. _explore_class:

Explore everything related to a class
-------------------------------------

Find all information related to a specific class, including its ancestors, descendants, associated properties as well as its usage

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: scls = se.get_class("GenomicEntity")

    In [5]: scls.describe()

    Out [5]:{'properties': [{'class': 'GenomicEntity', 'properties': []},
                            {'class': 'MolecularEntity',
                             'properties': [SchemaProperty( name=molecularlyInteractsWith),
                                            SchemaProperty(name=affectsAbundanceOf),
                                            SchemaProperty(name=increasesAbundanceOf),
                                            SchemaProperty(name=decreasesAbundanceOf),
                                            ......
                                            SchemaProperty(name=decreasesUptakeOf),
                                            SchemaProperty(name=regulates,EntityToEntity),
                                            SchemaProperty(name=biomarkerFor)]},
                            {'class': 'BiologicalEntity',
                             'properties': [SchemaProperty(name=hasPhenotype)]},
                            {'class': 'Thing',
                             'properties': [SchemaProperty(name=sameAs),
                                            SchemaProperty(name=alternateName),
                                            SchemaProperty(name=image),
                                            SchemaProperty(name=additionalType),
                                            SchemaProperty(name=name),
                                            SchemaProperty(name=identifier),
                                            SchemaProperty(name=subjectOf),
                                            SchemaProperty(name=mainEntityOfPage),
                                            SchemaProperty(name=url),
                                            SchemaProperty(name=potentialAction),
                                            SchemaProperty(name=description),
                                            SchemaProperty(name=disambiguatingDescription)]}],
             'description': 'an entity that can either be directly located on a genome (gene, transcript, exon, regulatory region) or is encoded in a genome (protein)',
             'uri': 'http://schema.biothings.io/GenomicEntity',
             'usage': [{'property': SchemaProperty(name=affectsExpressionOf),
                        'property_used_on_class': SchemaClass(name=MolecularEntity),
                        'description': 'holds between two molecular entities where the action or effect of one changes the level of expression of the other within a system of interest'},
                       {'property': SchemaProperty(name=increasesExpressionOf),
                        'property_used_on_class': SchemaClass(name=MolecularEntity),
                        'description': 'holds between two molecular entities where the action or effect of one increases the level of expression of the other within a system of interest'},
                       {'property': SchemaProperty(name=decreasesExpressionOf),
                        'property_used_on_class': SchemaClass(name=MolecularEntity),
                        'description': 'holds between two molecular entities where the action or effect of one decreases the level of expression of the other within a system of interest'},
                       {'property': SchemaProperty(name=affectsMutationRateOf),
                        'property_used_on_class': SchemaClass(name=MolecularEntity),
                        'description': 'holds between a molecular entity and a genomic entity where the action or effect of the molecular entity impacts the rate of mutation of the genomic entity within a system of interest'},
                       {'property': SchemaProperty(name=increasesMutationRateOf),
                        'property_used_on_class': SchemaClass(name=MolecularEntity),
                        'description': 'holds between a molecular entity and a genomic entity where the action or effect of the molecular entity increases the rate of mutation of the genomic entity within a system of interest'},
                       {'property': SchemaProperty(name=decreasesMutationRateOf),
                        'property_used_on_class': SchemaClass(name=MolecularEntity),
                        'description': 'holds between a molecular entity and a genomic entity where the action or effect of the molecular entity decreases the rate of mutation of the genomic entity within a system of interest'}],
             'child_classes': [SchemaClass(name=Genome),
                               SchemaClass(name=Transcript),
                               SchemaClass(name=Exon),
                               SchemaClass(name=CodingSequence),
                               SchemaClass(name=MacromolecularMachine),
                               SchemaClass(name=Genotype),
                               SchemaClass(name=Haplotype),
                               SchemaClass(name=SequenceVariant)],
             'parent_classes': [[SchemaClass(name=Thing),
                                 SchemaClass(name=BiologicalEntity),
                                 SchemaClass(name=MolecularEntity)]]}

.. _find_parent_properties:

Find all parents of a specific property
---------------------------------------

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: sp = se.get_property("ensembl")

    In [5]: sp.parent_properties

    Out [5]: [SchemaClass(name=identifier)]

.. _find_child_properties:

Find all children of a specific property
----------------------------------------

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: sp = se.get_property("ensembl")

    In [5]: sp.child_properties

    Out [5]: [SchemaClass(name=ensembl),
              SchemaClass(name=hgnc),
              SchemaClass(name=mgi),
              SchemaClass(name=rgd),
              SchemaClass(name=zfin),
              SchemaClass(name=flybase),
              ......,
              SchemaClass(name=unigene),
              SchemaClass(name=inchi),
              SchemaClass(name=inchikey),
              SchemaClass(name=rxcui),
              SchemaClass(name=smiles),
              SchemaClass(name=pubchem),
              SchemaClass(name=chembl),
              SchemaClass(name=drugbank),
              SchemaClass(name=unii)]

.. _explore_property:

Explore everything related to a property
----------------------------------------

Find all information related to a specific property, including its ancestors, descendants, etc.

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [3]: se = Schema(schema=schema_url)

    In [4]: sp = se.get_property("ensembl")

    In [5]: sp.describe()

    Out [5]: {'child_properties': [],
              'descendant_properties': [],
              'parent_properties': [SchemaClass(name=identifier)],
              'id': 'ensembl',
              'description': 'Ensembl ID for gene, protein or transcript',
              'domain': [SchemaClass(name=GeneOrGeneProduct),
                         SchemaClass(name=Transcript)],
             'range': SchemaClass(name=Text)}