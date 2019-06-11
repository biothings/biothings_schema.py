.. biothings_schema documentation master file, created by
   sphinx-quickstart on Wed Jun  5 14:18:13 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to biothings_schema's documentation!
============================================
biothings_schema is a Python package for the creation, extension and exploration of the schemas defined using the `Schema.org <https://www.schema.org/>`_ standard.

Our Beloved Features
--------------------

- Visulize schema structure
- Find parents/children of a schema class
- Find properties associated with a schema class
- Validate your schema against JSON schema
- Edit your schema

Audience
--------

The audience for biothings_schema python package includes developers interested in **consuming and extending** the schema defined by `Schema.org <https://www.schema.org/>`_.

Schema.org and biothings_schema
-------------------------------
Schema.org is a collaborative, community activity with a mission to create, maintain, and promote schemas for structured data on the Internet, on web pages, in email messages, and beyond.

In addition, schema.org offers the ability to extend the existing vocabulary, so that third-parties could specify additional properties or sub-types to existing types.

biothings_schema python package allows users to easily explore and consume the existing vocabularies defined in the schema.org. It also helps users to extend the schema.org vocabularies.

For more information related to schema.org, please refer to `<https://www.schema.org/>`_ 


Tutorials
---------
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   doc/load
   doc/visualize
   doc/explore
   doc/validate


Installation
------------

To install biothings_schema, simply use pip:

    Option 1
          install the latest code directly from the repository::

            pip install git+https://github.com/biothings/biothings_schema.py#egg=biothings_schema.py


