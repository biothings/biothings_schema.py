.. How to load external schema

Load External Schema
********************

Currently, biothings_schema pyton package can handle 3 types of input:

1. A JSON document represented as a python dict

2. A URL to the JSON/YAML document

3. A file path to the JSON/YAML document

.. _load_from_python_dictionary:

Use Python Dictionary as Input
------------------------------

biothings_schema python package accepts a JSON document as its input

.. code-block:: python

    In [1]: from biothings_schema import Schema

    In [2]: schema = {
                "@context": {
                    "bts": "http://schema.biothings.io/",
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "schema": "http://schema.org/",
                    "xsd": "http://www.w3.org/2001/XMLSchema#"
                },
                "@graph": [
                    {
                        "@id": "bts:BiologicalEntity",
                        "@type": "rdfs:Class",
                        "rdfs:comment": "biological entity",
                        "rdfs:label": "BiologicalEntity",
                        "rdfs:subClassOf": {
                            "@id": "schema:Thing"
                        },
                        "schema:isPartOf": {
                            "@id": "http://schema.biothings.io"
                        }
                    },
                    {
                        "@id": "bts:affectsAbundanceOf",
                        "@type": "rdf:Property",
                        "rdfs:comment": "affects abundance of",
                        "rdfs:label": "affectsAbundanceOf",
                        "schema:domainIncludes": {
                            "@id": "bts:BiologicalEntity"
                        },
                        "schema:isPartOf": {
                            "@id": "http://schema.biothings.io"
                        },
                        "schema:rangeIncludes": {
                            "@id": "bts:BiologicalEntity"
                        }
                    }
                ],
                "@id": "http://schema.biothings.io/#0.1"
            }
    In [3]: se = Schema(schema=schema)


.. _load_from_url:

Use URL as Input
-----------------

biothings_schema python package also accepts URL as its input. The data loaded from the URL must be either a JSON document or a YAML document.

.. code-block:: python

    In [1]: schema_url = 'https://raw.githubusercontent.com/data2health/schemas/biothings/biothings/biothings_curie_kevin.jsonld'

    In [2]: se = Schema(schema=schema_url)

.. _load_from_file_path:

Use Local File Path as Input
----------------------------

biothings_schema python package also accepts local file path as its input. The data loaded from the local file path must be either a JSON document or a YAML document.

.. code-block:: python

    In [1]: schema_path = '../data/schema.jsonld'

    In [2]: se = Schema(schema=schema_path)
