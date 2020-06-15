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

See :doc:`context` to find available context.

.. _concurrent-running:

Concurrent running
------------------
To reduce runtime, Preacher can run scenarios concurrently
by ``-c`` or ``--concurrency`` options The default is ``1`` (run serially.)

By default, the running unit is each scenario: cases are run in order, not concurrently.
When given ``ordered: false`` to a scenario,
then the cases of the scenario will be run concurrently.

.. code-block:: yaml

    label: Unordered cases.
    ordered: false
    cases:
      # These cases can be run concurrently.
      - label: Case 1
        ...
      - label: Case 2
        ...

Allowing Random Errors
----------------------
Web API cannot always responds due to communication errors and so on.
To allow these errors to some extent, Preacher supports retrying.
you can set the retry count by ``-r`` or ``--retry`` options.
The default is ``0`` (no retry.)

.. note:: Preacher retries while not only request fails but also a validation doesn't succeed.

Extreme response delaying can affect the testing process.
You can set the timeout by ``-t`` or ``--timeout`` options (in seconds).
The default is none (no timeout.)

Retrying should have intervals to avoid overloading.
You can set the retry interval (in seconds)
by ``-d`` or ``--delay`` options.
The default is ``0.1``.

Control Outputs
---------------
By default, not ``SKIPPED`` test results are shown.
It is useful for debugging your test cases,
but will be noisy when your test scenarios become huge.
The output level control will help you find important errors.

.. code-block:: sh

    $ preacher-cli --level unstable scenario.yml

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
