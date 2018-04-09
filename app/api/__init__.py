from flask import Blueprint, Response, json, Flask, current_app, request


class ApiResult:
    """Common api result type."""

    def __init__(self, value, status=200):
        self.value = value
        self.status = status

    def to_response(self) -> Response:
        return Response(response=json.dumps(self.value),
                        status=self.status,
                        mimetype='application/json')


class ApiException(Exception):
    """Common api exception type."""

    def __init__(self, value, status=400):
        self.value = value
        self.status = status

        current_app.logger.warning(
            f"'{self}' generated for request [{request.method}] with json payload '{request.get_json()}'")

    def to_result(self) -> ApiResult:
        return ApiResult({'message': self.value}, status=self.status)


class ApiFlask(Flask):
    """Flask response converter aware of ApiResult."""

    def make_response(self, rv) -> Response:
        if isinstance(rv, ApiResult):
            return rv.to_response()

        return Flask.make_response(self, rv)


bp = Blueprint('api', __name__)

from app.api import models, routes, error_handlers
