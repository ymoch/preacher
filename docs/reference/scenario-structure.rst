Scenario Structure
==================
Let's take a look at the structure of verification scenario.

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
      - label: A simple example
        request: /path/to/foo?bar=baz
        response:
          status_code: 200
          body:
            - describe: .foo
              should:
                equal: bar
      - label: A Little Complicated
        enabled: true
        request:
          method: POST
          path: /path/to/foo
          headers:
            user-agent: custom-value
          params:
            key1: value
            key2:
              - value1
              - value2
          body:
            type: urlencoded
            data:
              foo: bar
        response:
          status_code:
            - be_greater_than_or_equal_to: 200
            - be_less_than: 400
          headers:
            - describe: ."content-type"
              should:
                equal_to: application/xml
            - describe:
                jq: ."content-length"
                cast_to: int
              should:
                be_greater_than: 100
          body:
            analyzed_as: xml
            descriptions:
              - describe:
                  xpath: /html/body/h1
                should:
                  - start_with: x
                  - end_with: y

Scenario
--------
A "scenario" is the basic unit of verification process.
A scenario contains some "cases", which are basically run serially.
Scenarios can be nested by using "subscenarios."

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
    * - cases
      - List[:ref:`case`]
      - ``[]``
      - Test cases.
    * - subscenarios
      - List[Scenario]
      - ``[]``
      - Nested scenarios.
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
      - List[:ref:`description`]
      - ``[]``
      - Run this scenario only when the context satisfies these description.
        See :doc:`context` for more information.
    * - parameters
      - List[:ref:`parameter`]
      - ``null``
      - Parameters to make parameterized test.
        See :ref:`parameterized-test` for more information.

Minimally, a scenario should contain ``label`` and ``cases``.

.. code-block:: yaml

    label: The label of this scenario
    cases:
      - ...
      - ...

Only the top level YAML value can be a list,
which will be flattened even if it is nested.

.. code-block:: yaml

    - label: The label of the 1st scenario
      cases:
        - ...
    - - label: The label of the 2nd scenario
        cases:
          - ...
      - label: The label of the 3rd scenario
        cases:
          - ...

Only the top level YAML value can also be a YAML stream,
which has zero or more documents.

.. code-block:: yaml

    ---
    label: The label of the 1st scenario
    cases:
      - ...
    ---
    - label: The label of the 2nd scenario
      cases:
        - ...
    - label: The label of the 3rd scenario
      cases:
        - ...

.. _case:

Case
----
A "case" is the basic unit of verification, which executes a request and verify its response.

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
    * - request
      - :ref:`request`
      - :ref:`The default request <default-test>`
      - The request to be executed in this case.
    * - response
      - :ref:`response-description`
      - :ref:`The default response description<default-test>`
      - The response description of this case.
    * - enabled
      - Boolean
      - ``true``
      - Whether this case is enabled. See :ref:`ignore-cases` for more information.
    * - when
      - List[Description]
      - ``[]``
      - Run this case only when the context satisfies these description.
        See :doc:`context` for more information.

You can use default values to simplify cases. See :ref:`default-test` for more information.

.. _request:

Request
-------
Normally, a "request" is described in a form of a dictionary.
When given only a string, that is equivalent to ``{path: it}``.

.. list-table::
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - method
      - String
      - ``GET``
      - An HTTP method,
        which must be in ``GET``, ``POST``, ``PUT`` or ``DELETE``.
    * - path
      - String
      - ``''``
      - A request path
    * - headers
      - Map[String, String]
      - ``{}``
      - The headers as a map of names to values.
    * - params
      - :ref:`url-parameters`
      - ``{}``
      - The URL parameters for the query string.
    * - body
      - :ref:`request-body`
      - ``null``
      - The request body.

.. note:: A request path can also contain query parameters like ``/path?foo=bar&spam=ham``.

.. _url-parameters:

URLParameters
^^^^^^^^^^^^^
When given URL parameters as a string, then it is regarded as a raw query string.

.. code-block:: yaml

    # Requests /path?foo=bar&foo=baz&spam=ham%26eggs
    request:
      path: /path
      params: foo=bar&foo=baz&spam=ham%26eggs

When given URL parameters as a dictionary,
then it is regarded as a map of keys to values and the query string is built with it.

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

.. note:: Allowed types for the parameter values are integer, float, string, timestamp and null (ignored).
          A timestamp value is converted into IS0 8601 format.

.. _request-body:

RequestBody
^^^^^^^^^^^
.. list-table::
    :header-rows: 1
    :widths: 10 15 15 60

    * - Key
      - Type
      - Default
      - Description
    * - type
      - String
      - ``urlencoded``
      - The request body type, which is ``urlencoded`` or ``json``.
    * - data
      - Depends on the type
      - Depends on the type
      - The request body data.

When the type is ``urlencoded``,
the data are :ref:`url-parameters` and built into a URL-encoded value such that HTML forms send.
When the type is ``json``, the data are built into JSON.
The typical ``Content-type`` header will be set automatically.

.. _response-description:

ResponseDescription
-------------------
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
      - List[:ref:`description`]
      - ``null``
      - Descriptions that describe the response body.

.. _status-code:

Status code
^^^^^^^^^^^
When given a number, that is equivalent to ``{"equal": it}``.

.. _headers:

Headers
^^^^^^^
Response headers are converted to be a JSON
that is a map of names to values
and can be described as a JSON (e.g. ``."content-type"``).
*Note that Names are lower-cased* to normalize.

.. _description:

Description
-----------
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
---------
A ``Predicate`` is a :doc:`Matcher<matcher>` (can be extended in the future).

.. _parameter:

Parameter
---------
A "parameter" is a parameter in parameterized tests.
See :ref:`parameterized-test` for more information.

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
