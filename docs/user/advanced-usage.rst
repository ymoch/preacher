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

