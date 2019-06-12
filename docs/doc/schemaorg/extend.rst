.. Introduction of Schema.org

Extend Schema.org
*****************

Schema.org is a collaborative, community activity with a mission to create, maintain, and promote schemas for structured data on the Internet, on web pages, in email messages, and beyond.

.. _extend:

Extending Mechanism
-------------------

Over the years, we have experimented with a couple of different extension mechanisms (see 2011-2014 and 2014-2018 docs for details).

The primary motivation behind these models was to enable decentralized extension of the vocabulary. However, we have come to realize that for adoption, we need a simpler model, where publishers can be sure that a piece of vocabulary is indeed part of Schema.org. Until April 2019, we relied primarily on the 'hosted extensions' mechanism that used hosted subdomains of schema.org (such as bib.schema.org for the bibliography extension and autos.schema.org for the autos extension). Going forward, the content of these hosted extensions are being folded into schema.org, although each will retain an "entry point" page as before.

Terms from these hosted extensions are now considered fully part of schema.org, although they remain tagged with a label corresponding to the extension it originated from. Over a period of time, as usage of these terms gets intermingled with other terms, these labels may be dropped or simplified.

One label --- 'pending' --- is kept reserved for enabling us to more rapidly introduce terms into schema.org, on an experimental basis. After a period of time of being in a pending status, depending on usage, adoption, discussions etc. a term will be incorporated into the core or get dropped.

External extensions, where a third party might want to host a broadly applicable extension themselves (e.g., http://gs1.org/voc) will continue as before.

We continue to welcome improvements and additions to Schema.org, and to encourage public discussion towards this in various groups both at W3C and elsewhere. Additions to schema.org will now come in primarily via Pending. As always we place high emphasis on vocabulary that is likely to be consumed, rather than merely published.


How to Extend
-------------

You could extend Schema.org Schema by creating a subclass of an existing Schema.org Class or creating a subproperty of an existing Schema.org Property.
