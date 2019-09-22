========
Preacher
========

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/
.. image:: https://badge.fury.io/py/preacher.svg
    :target: https://badge.fury.io/py/preacher
.. image:: https://circleci.com/gh/ymoch/preacher.svg?style=svg
    :target: https://circleci.com/gh/ymoch/preacher
.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ymoch/preacher
.. image:: https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg
    :target: https://lgtm.com/projects/g/ymoch/preacher/context:python

Preacher verifies API servers,
which requests to API servers and verify the response along to given scenarios.

Scenarios are written in `YAML`_, bodies are analyzed `jq`_ or `XPath`_ queries
and validation rules are based on `Hamcrest (PyHamcrest)`_
so that any developers can write without learning toughly.


Development Policy
==================

Preacher aims to automate tests using real backends: neither mocks or sandboxes.
Supporting both automation and real backends has been challenging.

Preacher prefers:

- Flexible validation: Real backends causes fuzzy behavior.
  Matcher-based validation allow fuzziness caused by real backends.
- CI integration: CI tools are basic automation ways.
  CLI and YAML based test scenarios are suitable for CI.
- Simple GET requests: Testing with real backends often targets data fetching
  rather than HTTP interactions such as authorization.
  Development for complex HTTP interactions is less priored.

Comparing to other similar tools:

- `Postman <https://www.getpostman.com/>`_ gives rich insights on Web APIs.
  On the other hand, testing with CLI tools and configuration files is
  more suitable for CI automation.
- `Tavern <https://tavern.readthedocs.io/en/latest/>`_ is more suitable for testing
  HTTP interactions. It seems to be more suitable for testing simple systems
  or testing without real backends than Preacher because of simple validators.


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
          analyzed_as: json
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
          headers:
            user-agent: custom-value
          params:
            key1: value
            key2:
              - value1
              - value2
        response:
          status_code:
            - be_greater_than_or_equal_to: 200
            - be_less_than: 400
          headers:
            - describe: ."content-type"
              should:
                equal_to: application/xml
          body:
            analyzed_as: xml
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
- Headers: ``Mapping<String, String>`` (Optional)
    - Request headers as a mapping of names to values.
- params: ``Mapping<String, String>`` (Optional)
    - Query parameters as a mapping of keys to values.

When given a string, that is equivalent to ``{"path": it}``.

Response Decription
*******************
A ``ResponseDescription`` is a mapping that consists of below:

- status_code: ``Integer``, ``Predicate`` or ``List<Predicate>`` (Optional)
    - Predicates that match a status code as an integer value.
    - When given a number, that is equivalent to ``{"equal": it}``.
- headers:
    - Descriptions that descript the response headers.
    - Response headers are validated as a mapping of names to values
      and can be descripted by `jq_` query (e.g. ``."content-type"``).
      *Note that Names are lower-cased* to normalize.
- body: ``BodyDescription`` (Optional)
    - A description that descript the response body.

Body Description
****************
A ``BodyDescription`` is a mapping or a list.

A mapping for ``BodyDescription`` has items below.

- analyzed_as: ``String`` (Optional)
    - The method to analyze the body. The default value is ``json``.
    - When given ``json``, the body is analyzed as a JSON.
    - When given ``xml``, the body is analyzed as an XML.
- descriptions: ``Description`` or ``List<Description>``
    - Descriptions that descript the response body.

When given a list, that is equivalent to ``{"descritptions": it}``.

Description
***********
A ``Description`` is a mapping that consists of below:

- describe: ``Extraction``
    - An extraction process.
- should: ``Predicate``, or ``List<Predicate>>`` (Optional)
    - Predicates that match the descripted value.

Extraction
**********

An Extraction is a mapping or a string.

A mapping for Extraction has one of below:

- jq: String
    - A `jq`_ query.
- xpath: String
    - A `XPath`_ query

When given a string, that is equivalent to {"jq": it}.

Note that the extraction must be compatible for the body analysis.

+----------------------------+----+-------+
| Body Analysis / Extraction | jq | xpath |
+============================+====+=======+
| JSON                       |  o |     x |
+----------------------------+----+-------+
| XML                        |  x |     o |
+----------------------------+----+-------+

Predicate
*********
A ``Predicate`` is a ``Matcher`` (can be extended in the future).

Matcher
*******
A ``Matcher`` is a string or a mapping.

Allowed strings are:

- be_null: for an object
- not_be_null: for an object
- be_empty: for a sequence

A mapping for ``Matcher`` has an item. Allowed items are below.

.. note:: A ``Value`` given as a ``Matcher`` is equivalent to ``{"equal": it}``.

Object
======
- be: ``Matcher``
    - Matches matches the given matcher.
- not: ``Matcher``
    - Matches when it doesn't match the given matcher.
- equal: ``Value``
    - Matches when it equals the given value.
- have_length: ``Integer``
    - Matches when it has a length and its length is equal to the given value.

Comparable
==========
- be_greater_than: ``Comparable``
    - Matches when it is greater than the given value (it > argument).
- be_greater_than_or_equal_to: ``Comparable``
    - Matches when it is greater than or equal to the given value (it >= argument).
- be_less_than: ``Comparable``
    - Matches when it is less than the given value (it < argument).
- be_less_than_or_equal_to: ``Comparable``
    - Matches when it is less than or equal to the given value (it < argument).

String
======
- contain_string: ``String``
    - Matches when it is an string and contains the given value.
- start_with: ``String``
    - Matches when it is an string and starts with the given value.
- end_with: ``String``
    - Matches when it is an string and ends with the given value.
- match_regexp: ``String``
    - Matches when it is an string and matches the given regular expression.

Datetime
========
- be_before: ``String``
    - Matches when it is a datetime and before the given datetime.
    - When given ``now``, then compares to the datetime just when the request starts.
    - When given an offset, then compares to the datetime when the request starts.
        - Days, hours, minutes and seconds offsets are available.
        - When given a positive offset like ``1 day`` or ``+2 hours``,
          then compares to the future datetime.
        - When given a negative offset like ``-1 minute`` or ``-2 seconds``,
          then compares to the past datetime.
- be_after: ``String``
    - Matches when it is a datetime and after the given datetime.
    - Usage is the same as ``be_before``.

.. note:: Validated datetime values must be in ISO 8601 format
          like ``2019-01-23T12:34:56Z``.

Sequence
========
- have_item: ``Value`` or ``Matcher``
    - Matches when it is a collection and has the given item.
    - When given ``Value``, that is equivalent to ``{"equal": it}``.
- contain: ``List<Matcher>``
    - Exactly matches the entire sequence.
- contain_in_any_order: ``List<Matcher>``
    - Match the entire sequence, but in any order.


Default
*******
A ``Default`` is a mapping that consists of below:

- request: ``Request`` (Optional)
    - A request to overwrite the default request values.
- response: ``ResponseDescription`` (Optional)
    - A response description to overwrite the default response description values.

License
=======
.. image:: https://img.shields.io/badge/License-MIT-brightgreen.svg
    :target: https://opensource.org/licenses/MIT

.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
.. _Hamcrest (PyHamcrest): https://pyhamcrest.readthedocs.io/

Copyright (c) 2019 Yu MOCHIZUKI
