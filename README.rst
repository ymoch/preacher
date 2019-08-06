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

Scenarios are written in `YAML`_ and bodies are analyzed `jq`_ or `XPATH`_ queries
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

    label: Scenario example
    default:
      request:
        path: /path
      response:
        body:
          interpreted_as: json
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
            interpreted_as: xml
            descriptions:
              - describe: /html/body/h1
                should:
                  - start_with: x
                  - end_with: y

Grammer
-------

Scenario
********
A ``Scenario`` is written in `YAML`_.
A ``Scenario`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this scenario.
    - This field is actually optional but recommended to tell this scenario from another.
- default: ``Default`` (Optional)
    - Default of this scenario.
- cases: ``List<Case>``
    - Test cases.

Case
****
A ``Case`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this case.
    - This field is actually optional but recommended to tell this case from another.
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
- body: ``BodyDescription`` (Optional)
    - A description that descript the response body.

Body Description
****************
A ``BodyDescription`` is a mapping or a list.

A mapping for ``BodyDescription`` has items below.

- interpreted_as: ``String`` (Optional)
    - The method to interpret the body. The default value is ``json``.
    - When given ``json``, the body is interpreted as a JSON and analyzed by `jq`_ queries.
    - When given ``xml``, the body is interpreted as an XML and analyzed by `XPATH`_ queries.
- descriptions: ``Description`` or ``List<Description>``

When given a list, that is equivalent to ``{"descritptions": it}``.

Description
***********
A ``Description`` is a mapping that consists of below:

- describe: ``String``
    - An analysis as a `jq`_ or an `XPATH`_ query to find the descripted value.
- should: ``Predicate``, or ``List<Predicate>>`` (Optional)
    - Predicates that match the descripted value.

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

Default
*******
A ``Default`` is a mapping that consists of below:

- request: ``Request`` (Optional)
    - A request to overwrite the default request values.
- response: ``ResponseDescription`` (Optional)
    - A response description to overwrite the default response description values.

.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
.. _pipenv: https://pipenv.readthedocs.io/
