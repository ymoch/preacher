import os

import jinja2

from preacher.core.scenario import ScenarioResult


class ReportingListener:

    def __init__(self, path):
        self._path = path
        self._results = []

        os.makedirs(self._path, exist_ok=True)

    def accept(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def end(self) -> None:
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('preacher', 'resources/html'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        html_path = os.path.join(self._path, 'index.html')
        with open(html_path, 'w') as f:
            env.get_template('index.html').stream(
                scenarios=self._results,
            ).dump(f)
