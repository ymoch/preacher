Application Running Context
===========================
You can toggle scenarios using application running context.

Conditional Scenario
--------------------
Using ``when`` properties, you can run scenarios conditionally.
Scenarios are run only when the context satisfied the descriptions
in ``when`` properties.

.. code-block:: yaml

    # scenario.yml
    label: Conditional Scenario Example
    when:
      - describe: .base_url
        should:
          contain_string: localhost
    cases:
      - (Case definitions...)


Definition
----------
A ``Context`` is a JSON-like value, which can be descripted by `jq`_
Here is the definition of ``Context`` Object.

.. list-table:: The definition of ``Context`` Object
   :header-rows: 1
   :widths: 15 15 40 30

   * - Key
     - Type
     - Description
     - Example
   * - base_url
     - string
     - Base URL
     - http://localhost:5042/base


.. _jq: https://stedolan.github.io/jq/
