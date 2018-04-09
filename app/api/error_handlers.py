from app.api import bp, ApiException


@bp.errorhandler(ApiException)
def handle_api_exception(error):
    return error.to_result()
