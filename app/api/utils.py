import functools

import jwt
from flask import request, current_app
from voluptuous import Invalid, Schema

from app.api import ApiException


def api_schema(schema: Schema):
    """Validates current request with passed schema.

    If request satisfies it, fields are passed as additional arguments to a function.

    Args:
        schema: schema to validate request against.

    Returns:
        Wrapped function with additional arguments extracted from request.

    Raises:
        ApiException if schema is not satisfied.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            try:
                kwargs.update(schema(request.get_json()))
            except Invalid as e:
                raise ApiException("Invalid data format: '{}' (path: {})".format(e.msg, '.'.join(e.path)))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def token_required(f):
    """Validates token in current request.

    Passes decoded token data as additional argument of wrapped function.

    Args:
        f: wrapped function which will receive token data.

    Raises:
        ApiException if token is malformed or not present.

    Returns:
        Wrapped function with additional argument with token data.
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'x-access-token' not in request.headers:
            raise ApiException("Missing token in 'x-access-token' header")

        token = request.headers['x-access-token']

        try:
            token_data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except jwt.DecodeError:
            raise ApiException("JWT is malformed")

        return f(token_data, *args, **kwargs)

    return decorated
