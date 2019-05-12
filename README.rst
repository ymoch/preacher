========
Preacher
========

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/
.. image:: https://badge.fury.io/py/preacher.svg
    :target: https://badge.fury.io/py/preacher
.. image:: https://travis-ci.org/ymoch/preacher.svg?branch=master
    :target: https://travis-ci.org/ymoch/preacher
.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ymoch/preacher
.. image:: https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg
    :target: https://lgtm.com/projects/g/ymoch/preacher/context:python

Preacher verifies API servers,
which requests to API servers and verify the response along to given scenarios.

Scenarios are written in `YAML`_ and `jq`_ queries
so that any developers can write without learning toughly.


Usage
=====

Requirements
------------
Supports only Python 3.7+.

.. code-block:: sh

    pip install preacher
    preacher-cli scenario.yml

    # Help command is available.
    preacher-cli --help


Writing Your Own Scenarios
==========================

Example
-------
Here is a simple configuration example.

.. code-block:: yaml

    cases:
      - label: Simple
        request: /path/to/foo
        response:
          status_code: 200
          body:
            - describe: .foo
              should:
                equal: bar
      - label: A Little Complecated
        request:
          path: /path/to/foo
          params:
            key1: value
            key2:
              - value1
              - value2
        response:
          status_code:
            - be_greater_than_or_equal_to: 200
            - be_less_than: 400
          body:
            - describe:
                jq: .foo
              should:
                - start_with: x
                - end_with: y

Grammer
-------

Global
******
A ``Scenario`` is written in `YAML`_.
A ``Scenario`` is a mapping that consists of below:

- cases: ``List<Case>``
    - Test cases.

Case
****
A ``Case`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this case.
    - This field is actually optional but recommended to tell a case from another.
- request: ``Request`` (Optional)
    - A request.
- response: ``ResponseDescription`` (Optional)
    - A response description.

Request
*******
A ``Request`` is a mapping or a string.

A mapping for ``Request`` has items below:

- path: ``String`` (Optional)
    - A request path. The default value is ``''``.
- params: ``Mapping<String, String>`` (Optional)
    - Query parameters as a mapping of keys to values.

When given a string, that is equivalent to ``{"path": it}``.

Response Decription
*******************
A ``ResponseDescription`` is a mapping that consists of below:

- status_code: ``Integer``, ``Predicate`` or ``List<Predicate>`` (Optional)
    - Predicates that match a status code as an integer value.
    - When given a number, that is equivalent to ``{"equal": it}``.
- body: ``Description`` or ``List<Description>`` (Optional)
    - Descriptions that descript the response body.

Description
***********
A ``Description`` is a mapping that consists of below:

- describe: ``String`` or ``Extraction``
    - An extraction process.
    - When given a string, that is equivalent to ``{"jq": it}``.
- should: ``Predicate``, or ``List<Predicate>>`` (Optional)
    - Predicates that match the extracted value.

Extraction
**********
An ``Extraction`` is a mapping or a string.

A mapping for ``Extraction`` has one of below:

- jq: ``String``
    - A `jq`_ query.

When fiven a string, that is equivalent to ``{"jq": it}``.

Predicate
*********
A ``Predicate`` is a ``Matcher`` (can be extended in the future).

Matcher
*******
A ``Matcher`` is a string or a mapping.

Allowed strings are:

- be_null
- not_be_null
- be_empty

A mapping for ``Matcher`` has an item. Allowed items are:

- be: ``Value`` or ``Matcher``
    - Matches when it matches the given value or the given matcher.
    - When given ``Value``, that is equivalent to ``{"equal": it}``.
- not: ``Value`` or ``Matcher``
    - Matches when it doesn't match the given value or the given matcher.
    - When given ``Value``, that is equivalent to ``{"not": {"equal": it}}``
- equal: ``Value``
    - Matches when it equals the given value.
- have_length: ``Integer``
    - Matches when it has a length and its length is equal to the given value.
- be_greater_than: ``Comparable``
    - Matches when it is greater than the given value (it > argument).
- be_greater_than_or_equal_to: ``Comparable``
    - Matches when it is greater than or equal to the given value (it >= argument).
- be_less_than: ``Comparable``
    - Matches when it is less than the given value (it < argument).
- be_less_than_or_equal_to: ``Comparable``
    - Matches when it is less than or equal to the given value (it < argument).
- contain_string: ``String``
    - Matches when it is an string and contains the given value.
- start_with: ``String``
    - Matches when it is an string and starts with the given value.
- end_with: ``String``
    - Matches when it is an string and ends with the given value.
- match_regexp: ``String``
    - Matches when it is an string and matches the given regular expression.
- have_item: ``Value`` or ``Matcher``
    - Matches when it is a collection and has the given item.
    - When given ``Value``, that is equivalent to ``{"equal": it}``.


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _pipenv: https://pipenv.readthedocs.io/
