from .request import RequestCompiler
from .request_body import RequestBodyCompiler


def create_request_compiler() -> RequestCompiler:
    body = RequestBodyCompiler()
    return RequestCompiler(body=body)
