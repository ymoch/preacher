Advanced Usage
==============

.. _default-test:

Default Test
------------
Default test make it possible to run similar tests,
which fills the missing values with default values.

.. code-block:: yaml

    label: Default test examples.
    default:
      request:
        path: /default/path
      response:
        status_code: 200
    cases:
      - label: Request /default/path?foo=bar and test the status is 200.
        request:
          # path: /default/path
          params:
            foo: bar
        # response
        #   status_code: 200
      - label: Request /path and test the status is 404.
        request:
          path: /path  # overwrites the default value.
        response:
          status_code: 404
    subscenarios:
      - label: A subscenario of a default test.
        default:
          # Overwrites the default value.
          request:
            params:
              spam: ham
          response:
            status_code: 400
        cases:
          - label: Request /default/path?spam=ham and test the status is 400.
            # requests:
            #   path: /default/path
            #   params:
            #     spam: ham
            # response:
            #   status_code: 400

.. _parameterized-test:

Parameterized Test
------------------
Parameterized tests make it possible to run a test multiple times with different arguments,
which can reduce test scenarios description and make them simpler and more declarative.

To make tests parameterized:

- Define ``parameters`` field.
- Set ``!argument`` tag and its key on parameterized fields.

.. code-block:: yaml

    label: Parameterized test example.
    parameters:
      - label: parameter 1
        args:
          foo: a string
          bar: 1.23
      - label: Parameter 2
        args:
          foo: another string
          bar: 4.56
    cases:
      - request:
          path: /path/to/an/api
          params:
            - foo: !argument foo
        response:
          body:
            - describe: .bar
              should:
                equal_to: !argument bar

Conditional Scenario
--------------------
Using ``when`` properties, you can run scenarios conditionally.
Scenarios are run only when the *context* satisfied the descriptions
in ``when`` properties.

.. code-block:: yaml

    label: Run this scenario only for localhost.
    when:
      - describe:
          key: base_url
        should:
          contain_string: localhost
      - describe:
          jq: .starts  # can be analyzed as a JSON and extracted with a "jq".
    cases:
      - ...

See :doc:`../reference/context` to find available context.

.. _ignore-cases:

Ignore cases
------------
To skip some cases temporarily for some reason,
add ``enabled: false`` to that cases.

.. code-block:: yaml

    cases:
      - label: Disabled case
        enabled: false
        request: ...

.. _jq: https://stedolan.github.io/jq/
