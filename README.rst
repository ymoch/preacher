Preacher
========

.. image:: https://travis-ci.org/ymoch/preacher.svg?branch=master
    :target: https://travis-ci.org/ymoch/preacher
.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ymoch/preacher
.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/

A Web API verification tool.

Grammer
-------

Response Decriptions
********************
A ``ResponseDescription`` is a mapping that consists of below:

- status_code: ``Integer``, ``Predicate`` or ``List<Predicate>`` (Optional)
    - Predicates that match a status code as an integer value.
    - When given a number, that is equivalent to ``{"equals_to": it}``.
- body: ``Description`` or ``List<Description>`` (Optional)
    - Descriptions that descript the response body.

Descriptions
************
A ``Description`` is a mapping that consists of below:

- value_of: ``String`` or ``Extraction``
    - An extraction process.
    - When given a string, that is passed to the default extraction.
- it: ``Predicate``, or ``List<Predicate>>``
    - Predicates that match the extracted value.

Extraction
**********
An ``Extraction`` is a mapping that has one of below:

- jq: A `jq`_ query.

Predicates
**********
A ``Predicate`` is a string or a mapping. Allowed values are:

- is_null
- is_not_null
- is_empty
- is: ``Value``
- equals_to: ``Value``
- has_length: ``Integer``
- is_greater_than: ``Numeric``
- is_greater_than_or_equal_to: ``Numeric``
- is_less_than: ``Numeric``
- is_less_than_or_equal_to: ``Numeric``
- contains_string: ``String``
- starts_with: ``String``
- ends_with: ``String``
- matches_regexp: ``String``


.. _jq: https://stedolan.github.io/jq/
