import logging

from flask import jsonify

from utils.errors import AppError


_LOGGER = logging.getLogger(__name__)


def handle_app_error(error: AppError):
    """
    Handle expected application errors. The exception provides the HTTP status code and user-facing error message. 
    """

    return jsonify({
        "error_message": error.message

        }), error.status_code


def handle_unexpected_error(error: Exception):
    """
    Handle unexpected application errors. The full exception is logged internally, but the implementation details are not exposed to the client. 
    """

    _LOGGER.exception(
        "Unexpected application error: %s",
        error
        )

    return jsonify({
        "error_message": "An unexpected error occurred. Please try again later"
    }), 500

