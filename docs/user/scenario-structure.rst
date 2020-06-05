Scenario Structure
==================
In Preacher, a "scenario" is the basic unit of verification.

Example
-------
Here is a scenario example.

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
      - label: A Little Complicated
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
.. list-table::
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
    * - ordered
      - Boolean
      - ``true``
      - Mark the cases is ordered or not.
        When ``false``, cases can be run concurrently.
        See :ref:`concurrent-running` for more information.
    * - default
      - :ref:`case`
      - ``{}``
      - Default of this scenario.
        See :ref:`default-test` for more information.
    * - when
      - List[Description]
      - ``[]``
      - Run this scenario only when the context satisfies these description.
        See :doc:`Application Running Context<context>` for more information.
    * - cases
      - List[:ref:`case`]
      - ``[]``
      - Test cases.
    * - subscenarios
      - List[Scenario]
      - ``[]``
      - Nested scenarios.
    * - parameters
      - List[:ref:`parameter`]
      - ``null``
      - Parameters to make parameterized test.
        See :ref:`parameterized-test` for more information.

.. _parameter:

Parameter
^^^^^^^^^
.. list-table::
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - label
      - String
      - ``null``
      - Label of this parameter.
    * - args
      - Map
      - ``{}``
      - An argument map of argument names to their values.

See :ref:`parameterized-test` to check examples.

.. _case:

Case
^^^^
.. list-table::
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
.. list-table::
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
      - Map[String, String]
      - ``{}``
      - The headers as a map of names to values.
    * - params
      - :ref:`request-parameter`
      - ``{}``
      - Parameters for the query string.

When given a string as a ``Request``, that is equivalent to ``{path: it}``.

.. _request-parameter:

QueryParameter
""""""""""""""
When given a string, then it is regarded as a raw query string.

.. code-block:: yaml

    # Requests /path?foo=bar&foo=baz&spam=ham%26eggs
    request:
      path: /path
      params: foo=bar&foo=baz&spam=ham%26eggs

When given a map, then it is regarded as a map of keys to values
and the query string is built with it.

.. code-block:: yaml

    # Requests /path?foo=bar&foo=baz&spam=ham%26eggs
    request:
      path: /path
      params:
        foo:  # a value list is available.
          - bar
          - baz
          - null  # `null` is ignored
        spam: ham&eggs

.. note:: Allowed types for the parameter values are integer, float, string and null (ignored).

.. _response-description:

ResponseDescription
^^^^^^^^^^^^^^^^^^^
.. list-table::
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
that is a map of names to values
and can be described as a JSON (e.g. ``."content-type"``).
*Note that Names are lower-cased* to normalize.

.. _body-description:

BodyDescription
^^^^^^^^^^^^^^^
.. list-table::
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - analyze_as
      - String
      - ``json``
      - The method to analyze the body.
        Allowed values are ``json`` and ``xml``.
    * - descriptions
      - List[:ref:`description`]
      - ``[]``
      - Descriptions that describe the response body.

When given a list as a ``BodyDescription``,
that is equivalent to ``{"descritptions": it}``.

.. _description:

Description
^^^^^^^^^^^
.. list-table::
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - describe
      - :doc:`Extraction<extraction>`
      - **Required**
      - An extraction to get the described value.
    * - should
      - List[:ref:`predicate`]
      - ``{}``
      - Predicates that match the described value.

.. _predicate:

Predicate
^^^^^^^^^
A ``Predicate`` is a :doc:`Matcher<matcher>` (can be extended in the future).

Including other files
---------------------
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

UNIX-like wildcard expansion is available.
A wildcard inclusion results in the list of matching inclusion.

.. code-block:: yaml

    !include path/to/*.yml

.. note:: Anchors in a included YAML are not available in including YAMLs,
          because the included YAMLs are parsed after the including YAML is parsed.

.. note:: Names of included files should not contain any wildcard characters
          because not all of the wildcard expansion rules are covered.

.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
