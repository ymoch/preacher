========
Preacher
========

.. image:: https://travis-ci.org/ymoch/preacher.svg?branch=master
    :target: https://travis-ci.org/ymoch/preacher
.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ymoch/preacher
.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/

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
        request:
          path: /path/to/foo
        response:
          status_code: 200
          body:
            - describe:
                jq: .foo
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
                - ends_wirh: y

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
A ``Request`` is a mapping that consists of below:

- path: ``String`` (Optional)
    - A request path. The default value is ``''``.
- params: ``Mapping<String, String>`` (Optional)
    - Query parameters as a mapping of keys to values.

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
    - When given a string, that is passed to the default extraction.
- it: ``Predicate``, or ``List<Predicate>>``
    - Predicates that match the extracted value.

Extraction
**********
An ``Extraction`` is a mapping that has one of below:

- jq: ``String``
    - A `jq`_ query.

Predicate
*********
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


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
