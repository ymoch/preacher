Advanced Usage
==============

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

Ignore cases
------------
To skip some cases temporarily for some reason,
add ``enabled: false`` to that cases.

.. code-block:: yaml

    cases:
      - label: Disabled case
        enabled: false
        request: ...

Conditional Scenario
--------------------
Using ``when`` properties, you can run scenarios conditionally.
Scenarios are run only when the *context* satisfied the descriptions
in ``when`` properties.

.. code-block:: yaml

    label: Run this scenario only for localhost.
    when:
      - describe: .app.base_url
        should:
          contain_string: localhost
    cases:
      - ...

A ``Context`` object, which stands for *context*, is a JSON-like value,
which can be descripted by `jq`_.
See :doc:`context` to find available context.

Parameterized Test
------------------
Parameterized tests make it possible to run a test multiple times with different arguments,
which can reduce test scenarios description and make them simpler and more declarative.

To make tests parameterized:

- Define ``parameters`` as a list of key-value mapping.
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
                equal_to: !Parameter bar

.. _jq: https://stedolan.github.io/jq/
