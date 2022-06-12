Extraction
==========
In Preacher, an "extraction" is a process to extract values from a target
such as a response body.
Extractions are descripted in `jq`_ or `XPath`_.

Grammer
-------

Full Definition
^^^^^^^^^^^^^^^
Here is the definition of ``Extraction`` as a mapping.

.. list-table:: The definition of ``Extraction`` Object
   :header-rows: 1

   * - Key
     - Type
     - Required?
     - Description
     - Example
   * - jq
     - string
     - ?
     - A `jq`_ query.
     - ``".foo.bar"``
   * - xpath
     - string
     - ?
     - A `XPath`_ query.
     - ``"/foo/nar"``
   * - key
     - string
     - ?
     - A key of a dictionary.
     - ``"key"``
   * - multiple
     - boolean
     - no
     - See: :ref:`multiple`
     - ``true``
   * - cast_to
     - string
     - no
     - See: :ref:`casting`
     - ``"float"``
   * - namespaces
     - dictionary
     - no (for XPath only)
     - A namespace mapping.
     - ``{"syn": "http://purl.org/rss/1.0/modules/syndication/"}``

.. note:: One of ``jq``, ``xpath`` or ``key`` is required.

.. _multiple:

Multiple Values
^^^^^^^^^^^^^^^
By default, an extraction provides the first of extracted values.
When ``multiple`` is  ``true``, it provides the list of all extracted values.

.. _casting:

Casting
^^^^^^^
Extracted values can be casted by ``cast_to`` settings.
This feature is useful for XML analysis,
which provides only strings even if they are numbers.

Allowed values are:

- int: Cast to an integer.
- float: Cast to a floating point number.
- string: Cast to a string.

.. note:: Casting does not affect ``null``.

Abbreviation
^^^^^^^^^^^^
Ordinary, extractions should be very simple `jq`_ queries.
In these cases, an extraction can be written in a string,
which is equivalent to ``{"jq": it}``.

Content Compatibility
---------------------
A extraction must be compatible for the content.

+----------------------+----+-------+-----+
| Content              | jq | xpath | key |
+======================+====+=======+=====+
| JSON (an object)     |  o |     x |   o |
+----------------------+----+-------+-----+
| JSON (not an object) |  o |     x |   x |
+----------------------+----+-------+-----+
| XML                  |  x |     o |   x |
+----------------------+----+-------+-----+


.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
