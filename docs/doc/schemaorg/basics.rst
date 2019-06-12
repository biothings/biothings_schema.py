.. Introduction of Schema.org

Schema.org Basics
******************

Schema.org is a collaborative, community activity with a mission to create, maintain, and promote schemas for structured data on the Internet, on web pages, in email messages, and beyond.

.. _two_main_types:

Classes and Properties
----------------------

Everything in Schema.org schema is either an item type/class or a property. For example, `Person <https://www.schema.org/Person>`_ is a schema.org Class. Every Class has its own properties. For example, `Address <https://www.schema.org/Address>`_ is a schema.org Property.

.. _hierarchical_structure:

Hierarchical Structure
----------------------

All classes in Schema.org schema is defined in a hierarchical tree structure. `Thing <https://www.schema.org/Thing>`_ is the root of this structure. And all classes besides `Thing <https://www.schema.org/Thing>`_ will have its own parent class(es) and may also have its own child class(es). For example, `Patient <https://www.schema.org/Patient>`_ is a subclass(child) of `Person <https://www.schema.org/Person>`_ and `Person <https://www.schema.org/Person>`_ is a subclass(child) of `Thing <https://www.schema.org/Thing>`_.

Moreover, properties could also have parent properties. For example, `isbn <https://www.schema.org/isbn>`_ is a subproperty(child) of `identifier <https://www.schema.org/identifier>`_.


.. _inheritance:

Inheritance
-----------
All classes defined in Schema.org schema will have its own specific properties. For example, `Address <https://www.schema.org/Address>`_ is a property of `Person <https://www.schema.org/Person>`_. In addition, all classes will inherit the properties of its ancestors. For example, `description <https://www.schema.org/description>`_ is a property of `Thing <https://www.schema.org/Thing>`_. And since `Person <https://www.schema.org/Person>`_ is a subclass(child) of `Thing <https://www.schema.org/Thing>`_, `Person <https://www.schema.org/Person>`_ inherit the property `description <https://www.schema.org/description>`_ from its parent `Thing <https://www.schema.org/Thing>`_.

