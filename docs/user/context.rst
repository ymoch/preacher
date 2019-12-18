Context Reference
=================

Scenario Context
----------------
.. list-table:: The definition of ``ScenarioContext`` Object
   :header-rows: 1
   :widths: 15 15 40 30

   * - Key
     - Type
     - Description
     - Example
   * - starts
     - DateTime
     - When the scenario starts
     - ``2019-01-23T12:34:56.123456+00:00``
   * - base_url
     - String
     - The base URL
     - ``http://localhost:5042/base``
   * - retry
     - Integer
     - The max retry count
     - 0
   * - delay
     - Float
     - The delay between attempts in seconds
     - 0.1
   * - timeout
     - Optional[Float]
     - The request timeout in seconds
     - ``null``, 1.0
