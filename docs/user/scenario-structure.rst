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
    when:
      - describe: .base_url
        should:
          contain_string: localhost
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
        enabled: true
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

.. list-table:: The Definition of ``Scenario`` Object
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - label
      - String
      - ``null``
      - A label of this scenario.
    * - default
      - :ref:`case`
      - ``{}``
      - Default of this scenario.
    * - when
      - List[Description]
      - ``[]``
      - | Run this scenario only when the context satisfies these description.
        | See: :doc:`Application Running Context<context>`
    * - cases
      - List[:ref:`Case`]
      - ``[]``
      - Test cases.
    * - subscenarios
      - List[Scenario]
      - ``[]``
      - Nested scenarios.

.. _case:

Case
^^^^
.. list-table:: The Definition of ``Case`` Object
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - label
      - String
      - ``null``
      - A label of this case.
    * - enabled
      - Boolean
      - ``true``
      - Whether this case is enabled.
    * - request
      - :ref:`request`
      - The default request
      - The request of this case.
    * - response
      - :ref:`response-description`
      - The default response description.
      - The response description of this case.

.. _request:

Request
^^^^^^^
.. list-table:: The Definition of ``Request`` Object
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - path
      - String
      - ``''``
      - A request path
    * - headers
      - Mapping[String, String]
      - ``{}``
      - The headers as a mapping of names to values.
    * - params
      - Mapping
      - ``{}``
      - Query parameters as a mapping of keys to values.

When given a string as a ``Request``, that is equivalent to ``{path: it}``.

.. _response-description:

ResponseDescription
^^^^^^^^^^^^^^^^^^^
.. list-table:: The Definition of ``ResponseDescription`` Object
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - status_code
      - List[:ref:`predicate`]
      - ``[]``
      - Predicates that match a status code as an integer value.
        See :ref:`status-code` for more information.
    * - headers
      - List[:ref:`description`]
      - ``{}``
      - Descriptions that describe the response headers.
        See :ref:`headers` for more information.
    * - body
      - :ref:`body-description`
      - ``null``
      - A description that describe the response body.

.. _status-code:

Status code
"""""""""""
When given a number, that is equivalent to ``{"equal": it}``.

.. _headers:

Headers
"""""""

Response headers are converted to be a JSON
that is a mapping of names to values
and can be descripted as a JSON (e.g. ``."content-type"``).
*Note that Names are lower-cased* to normalize.

.. _body-description:

BodyDescription
^^^^^^^^^^^^^^^
A ``BodyDescription`` is a mapping or a list.

A mapping for ``BodyDescription`` has items below.

- analyzed_as: ``String`` (Optional)
    - The method to analyze the body. The default value is ``json``.
    - When given ``json``, the body is analyzed as a JSON.
    - When given ``xml``, the body is analyzed as an XML.
- descriptions: ``Description`` or ``List<Description>``
    - Descriptions that descript the response body.

When given a list, that is equivalent to ``{"descritptions": it}``.

.. _description:

Description
^^^^^^^^^^^
A ``Description`` is a mapping that consists of below:

- describe: :doc:`Extraction<extraction>`
    - An extraction process.
- should: ``Predicate``, or ``List<Predicate>>`` (Optional)
    - Predicates that match the descripted value.

.. _predicate:

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

Inclusion
---------
Using ``!include`` tag, you can include other YAML files.
This macro is available anywhere in your scenario.

.. code-block:: yaml

    !include path/to/other.yaml

A good practice of this feature is locating subscenarios on subdirectories.

.. code-block:: yaml

    label: Subscenario inclusion example
    subscenarios:
      - !include subscenarios/subscenario1.yml
      - !include subscenarios/subscenario2.yml

.. note:: Anchors in a including YAML are not available in included YAMLs,
          because the included YAMLs are parsed after the including YAML is parsed.


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
