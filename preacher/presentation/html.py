import os
from typing import Iterable

import jinja2

from preacher.core.request import Response, ExecutionReport
from preacher.core.scenario import ScenarioResult


class HtmlReporter:
    def __init__(self, path):
        self._path = path
        self._responses_path = os.path.join(self._path, "responses")

        self._loader = jinja2.PackageLoader("preacher", "resources/report/html")

        self._initialize()

    def _initialize(self) -> None:
        os.makedirs(self._path, exist_ok=True)
        os.makedirs(self._responses_path, exist_ok=True)

    def export_response(self, execution: ExecutionReport, response: Response) -> None:
        name = f"{response.id}.html"
        path = os.path.join(self._responses_path, name)

        env = jinja2.Environment(loader=self._loader, autoescape=True)
        template = env.get_template("response-view.html")
        with open(path, "w") as f:
            template.stream(execution=execution, response=response).dump(f)

    def export_results(self, results: Iterable[ScenarioResult]) -> None:
        html_path = os.path.join(self._path, "index.html")

        env = jinja2.Environment(loader=self._loader, autoescape=True)
        template = env.get_template("index.html")
        with open(html_path, "w") as f:
            template.stream(scenarios=results).dump(f)
