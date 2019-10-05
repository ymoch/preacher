Quickstart
==========

Writing Your Own Scenarios
--------------------------
Here is a very simple example.

.. code-block:: yaml

    label: An example of a scenario
    cases:
      - label: An example of a case
        request: /path/to/foo
        response:
          status_code: 200
          body:
            - describe: .foo
              should:
                equal: bar

Verify the Servers
------------------

.. code-block:: sh

    $ preacher-cli -u https://your-server.com/base scenario.yml
