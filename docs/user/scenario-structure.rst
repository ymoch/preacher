Scenario Structure
==================
In Preacher, a "scenario" is the basic unit of verification.

Example
-------
Here is a configuration example.

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


Components
----------

Scenario
^^^^^^^^
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
^^^^
A ``Case`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this case.
    - This field is actually optional but recommended to tell this case from another.
- request: ``Request`` (Optional)
    - A request.
- response: ``ResponseDescription`` (Optional)
    - A response description.

Request
^^^^^^^
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
^^^^^^^^^^^^^^^^^^^
A ``ResponseDescription`` is a mapping that consists of below:

- status_code: ``Integer``, ``Predicate`` or ``List<Predicate>`` (Optional)
    - Predicates that match a status code as an integer value.
    - When given a number, that is equivalent to ``{"equal": it}``.
- headers:
    - Descriptions that descript the response headers.
    - Response headers are converted to be a JSON
      that is a mapping of names to values
      and can be descripted as a JSON (e.g. ``."content-type"``).
      *Note that Names are lower-cased* to normalize.
- body: ``BodyDescription`` (Optional)
    - A description that descript the response body.

Body Description
^^^^^^^^^^^^^^^^
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
^^^^^^^^^^^
A ``Description`` is a mapping that consists of below:

- describe: :doc:`Extraction<extraction>`
    - An extraction process.
- should: ``Predicate``, or ``List<Predicate>>`` (Optional)
    - Predicates that match the descripted value.

Predicate
^^^^^^^^^
A ``Predicate`` is a :doc:`Matcher<matcher>` (can be extended in the future).

Default
^^^^^^^
A ``Default`` is a mapping that consists of below:

- request: ``Request`` (Optional)
    - A request to overwrite the default request values.
- response: ``ResponseDescription`` (Optional)
    - A response description to overwrite the default response description values.

.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
