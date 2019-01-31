.. biothings_schema.py documentation master file, created by
   sphinx-quickstart on Wed Jan 30 15:48:16 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to biothings_schema.py's documentation!
===============================================
biothings_schema.py_ python package provides simple-to-use functions for users to visualize, edit and validate schemas defined using `Schema.org <http://schema.org/>`_ standard.
It's designed with simplicity and performance emphasized. *myvariant*, is an easy-to-use Python wrapper
to access MyVariant.Info_ services.

.. Note::
    As of v1.0.0, myvariant_ Python package is now a thin wrapper of underlying biothings_client_ package,
    a universal Python client for all `BioThings APIs <http://biothings.io>`_, including MyVariant.info_.
    The installation of myvariant_ will install biothings_client_ automatically. The following code snippets
    are essentially equivalent:

    * Continue using myvariant_ package

        .. code-block:: python

            In [1]: import myvariant
            In [2]: mv = myvariant.MyVariantInfo()

    * Use biothings_client_ package directly

        .. code-block:: python

            In [1]: from biothings_client import get_client
            In [2]: mv = get_client('variant')

    After that, the use of ``mv`` instance is exactly the same.
.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
