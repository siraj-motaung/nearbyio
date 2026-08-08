
import logging

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ExternalServiceError(AppError):
    pass


class ExternalServiceTimeout(AppError):
    pass

