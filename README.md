# Preacher: Web API Verification Valuing Automation and Reality

[![PyPI version](https://badge.fury.io/py/preacher.svg)](https://badge.fury.io/py/preacher)
[![Documentation Status](https://readthedocs.org/projects/preacher/badge/?version=latest)](https://preacher.readthedocs.io/en/latest/?badge=latest)
[![CircleCI](https://circleci.com/gh/ymoch/preacher.svg?style=svg)](https://circleci.com/gh/ymoch/preacher)
[![codecov](https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg)](https://codecov.io/gh/ymoch/preacher)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ymoch/preacher/context:python)

Preacher verifies API servers,
which requests to the servers and verify the responses along to given scenarios.

Scenarios are written in [YAML][], bodies are analyzed [jq][] or [XPath][] queries
and validation rules are based on [Hamcrest][] ([PyHamcrest][])
so that any developers can write without learning toughly.

The full documentation is available at [preacher.readthedocs.io][readthedocs].

## Targets

- Flexible validation to test with real backends: neither mocks nor sandboxes.
  - Matcher-based validation.
- CI Friendly to automate easily.
  - A CLI application and YAML-based scenarios.

## Usage

First, install Preacher.

The most basic way to install Preacher is using `pip`. Supports only Python 3.7+.

```sh
$ pip install preacher
$ preacher-cli --version
```

Instead of `pip`, Docker images are also available on
[Docker Hub](https://cloud.docker.com/u/ymoch/repository/docker/ymoch/preacher)
as `ymoch/preacher`.
Note that the working directory is `/work`
and the host directory should be mounted.

```sh
$ docker pull ymock/preacher
$ docker run -v $PWD:/work ymoch/preacher preacher-cli --version
```

Second, write your own scenario.

```yaml
# scenario.yml
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
```

Then, run ``preacher-cli`` command.

```sh
$ preacher-cli -u http://your.domain.com/base scenario.yml
```

For more information such as grammer of scenarios,
see [the full documentation][readthedocs].

## License

[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)][MIT License]

Copyright (c) 2019 Yu MOCHIZUKI


[YAML]: https://yaml.org/
[jq]: https://stedolan.github.io/jq/
[XPath]: https://www.w3.org/TR/xpath/all/
[Hamcrest]: http://hamcrest.org/
[PyHamcrest]: https://pyhamcrest.readthedocs.io/
[MIT License]: https://opensource.org/licenses/MIT
[readthedocs]: https://preacher.readthedocs.io/
