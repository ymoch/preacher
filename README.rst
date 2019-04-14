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

    scenarios:
      - label: Simple
        request: /path/to/foo
        response:
          status_code: 200
          body:
            - describe: .foo
              it:
                equals_to: bar
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
            - is_greater_than_or_equal_to: 200
            - is_less_than: 400
          body:
            - describe:
                jq: .foo
              it:
                - starts_with: x
                - ends_with: y

Grammer
-------

Global
******
A ``Configuration`` is written in `YAML`_.
A ``Configuration`` is a mapping that consists of below:

- scenarios: ``List<Scenario>``
    - Scenarios.

Scenario
********
A ``Scenario`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this scenario.
    - This field is actually optional but recommended to tell a scenario from another.
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
    - When given a number, that is equivalent to ``{"equals_to": it}``.
- body: ``Description`` or ``List<Description>`` (Optional)
    - Descriptions that descript the response body.

Description
***********
A ``Description`` is a mapping that consists of below:

- describe: ``String`` or ``Extraction``
    - An extraction process.
    - When given a string, that is equivalent to ``{"jq": it}``.
- it: ``Predicate``, or ``List<Predicate>>`` (Optional)
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

- is_null
- is_not_null
- is_empty

A mapping for ``Matcher`` has an item. Allowed items are:

- is: ``Value`` or ``Matcher``
    - Matches when it matches the given value or the given matcher.
    - When given ``Value``, that is equivalent to ``{"equals_to": it}``.
- not: ``Value`` or ``Matcher``
    - Matches when it doesn't match the given value or the given matcher.
    - When given ``Value``, that is equivalent to ``{"not": {"equals_to": it}}``
- equals_to: ``Value``
    - Matches when it equals to the given value.
- has_length: ``Integer``
    - Matches when it has a length and its length is equal to the given value.
- is_greater_than: ``Comparable``
    - Matches when it is greater than the given value (it > argument).
- is_greater_than_or_equal_to: ``Comparable``
    - Matches when it is greater than or equal to the given value (it >= argument).
- is_less_than: ``Comparable``
    - Matches when it is less than the given value (it < argument).
- is_less_than_or_equal_to: ``Comparable``
    - Matches when it is less than or equal to the given value (it < argument).
- contains_string: ``String``
    - Matches when it is an string and contains the given value.
- starts_with: ``String``
    - Matches when it is an string and starts with the given value.
- ends_with: ``String``
    - Matches when it is an string and ends with the given value.
- matches_regexp: ``String``
    - Matches when it is an string and matches the given regular expression.


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _pipenv: https://pipenv.readthedocs.io/
