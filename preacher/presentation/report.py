import os
from typing import Iterable

import jinja2

from preacher.core.request import Response, ExecutionReport
from preacher.core.scenario import ScenarioResult


class Reporter:

    def __init__(self, path):
        self._path = path
        self._responses_path = os.path.join(self._path, 'responses')

        loader = jinja2.PackageLoader('preacher', 'resources/report/html')
        env = jinja2.Environment(loader=loader, autoescape=True)
        self._index_template = env.get_template('index.html')
        self._response_view_template = env.get_template('response-view.html')

        self._initialize()

    def _initialize(self) -> None:
        os.makedirs(self._path, exist_ok=True)
        os.makedirs(self._responses_path, exist_ok=True)

    def export_execution(
        self,
        execution: ExecutionReport,
        response: Response,
    ) -> None:
        name = f'{response.id}.html'
        path = os.path.join(self._responses_path, name)
        with open(path, 'w') as f:
            self._response_view_template.stream(
                execution=execution,
                response=response,
            ).dump(f)

    def export_results(self, results: Iterable[ScenarioResult]) -> None:
        html_path = os.path.join(self._path, 'index.html')
        with open(html_path, 'w') as f:
            self._index_template.stream(scenarios=results).dump(f)
