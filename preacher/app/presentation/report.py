import os
from typing import Iterable

import jinja2

from preacher.core.response import Response
from preacher.core.scenario import ScenarioResult


class Reporter:

    def __init__(self, path):
        self._path = path
        self._responses_path = os.path.join(self._path, 'responses')

        env = jinja2.Environment(
            loader=jinja2.PackageLoader('preacher', 'resources/report/html'),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
        )
        self._index_template = env.get_template('index.html')
        self._response_view_template = env.get_template('response-view.html')

        self._initialize()

    def _initialize(self) -> None:
        os.makedirs(self._path, exist_ok=True)
        os.makedirs(self._responses_path, exist_ok=True)

    def export_response(self, response: Response) -> None:
        name = f'{response.id}.html'
        path = os.path.join(self._responses_path, name)
        with open(path, 'w') as f:
            self._response_view_template.stream(response=response).dump(f)

    def export_results(self, results: Iterable[ScenarioResult]) -> None:
        html_path = os.path.join(self._path, 'index.html')
        with open(html_path, 'w') as f:
            self._index_template.stream(scenarios=results).dump(f)
