Introduction
============

Targets
-------
Preacher aims to automate tests using real backends: neither mocks nor sandboxes.
Supporting both automation and real backends has been challenging.

Preacher prefers:

- Flexible validation: Real backends causes fuzzy behavior.
  Matcher-based validation allow fuzziness caused by real backends.
- CI friendship: CI tools are basic automation ways.
  CLI applications and YAML based test scenarios are suitable for CI.
- Simple GET requests: Testing with real backends often targets data fetching
  rather than HTTP interactions such as authorization.
  Development for complex HTTP interactions is less priored.

Comparison to similar tools
---------------------------

- `Postman`_ gives rich insights on Web APIs.
  On the other hand, testing with CLI applications and configuration files is
  more suitable for CI automation.
- `Tavern`_ is more suitable for testing HTTP interactions.
  It seems to be more suitable for testing simple systems
  or testing without real backends than Preacher because of simple validators.

License
-------

Preacher is released under terms of `MIT License`_.

    .. include:: ../../LICENSE

.. _Postman: https://www.getpostman.com/
.. _Tavern: https://tavern.readthedocs.io/en/latest/
.. _MIT License: https://opensource.org/licenses/MIT
