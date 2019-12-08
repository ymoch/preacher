Preacher: Web API Verification without Coding
=============================================

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/
.. image:: https://badge.fury.io/py/preacher.svg
    :target: https://badge.fury.io/py/preacher
.. image:: https://circleci.com/gh/ymoch/preacher.svg?style=svg
    :target: https://circleci.com/gh/ymoch/preacher
.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ymoch/preacher
.. image:: https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg
    :target: https://lgtm.com/projects/g/ymoch/preacher/context:python

Preacher verifies API servers,
which requests to API servers and verify the response along to given scenarios.

Test scenarios are written only in `YAML`_ declaratively, without coding.
In spite of that, Preacher can validate your web API flexibly,
which enables you to test using real (neither mocks nor sandboxes) backends.

- Responses are analyzed `jq`_ or `XPath`_ queries
- Validation rules are based on `Hamcrest`_ (implemented by `PyHamcrest`_).

The User Guide
--------------

.. toctree::
   :maxdepth: 2

   user/intro
   user/quickstart
   user/advanced-usage
   user/cli
   user/scenario-structure
   user/extraction
   user/matcher
   user/context


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
.. _Hamcrest: http://hamcrest.org/
.. _PyHamcrest: https://pyhamcrest.readthedocs.io/
