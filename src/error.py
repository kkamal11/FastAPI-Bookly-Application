from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class BooklyException(Exception):
    """Base exception class for Bookly application errors."""
    pass

class InvalidTokenError(BooklyException):
    """Exception raised for invalid authentication tokens."""
    pass

class RevokedTokenError(BooklyException):
    """Exception raised for revoked authentication tokens."""
    pass

class AccessTokenRequiredError(BooklyException):
    """Exception raised when an access token is required but not provided."""
    pass

class RefreshTokenRequiredError(BooklyException):
    """Exception raised when a refresh token is required but not provided."""
    pass

class UserAlreadyExistsError(BooklyException):
    """Exception raised when attempting to create a user that already exists."""
    pass

class UserNotFoundError(BooklyException):
    """Exception raised when a user is not found in the database."""
    pass

class InvalidCredentialsError(BooklyException):
    """Exception raised for invalid user credentials."""
    pass

class InsufficientPermissionsError(BooklyException):
    """Exception raised when a user lacks sufficient permissions for an action."""
    pass

class BookNotFoundError(BooklyException):
    """Exception raised when a book is not found in the database."""
    pass


class BookAlreadyExistsError(BooklyException):
    """Exception raised when attempting to create a book that already exists."""
    pass

def create_exception_handler(status_code: int, detail: Any) -> Callable[[Request, Exception],JSONResponse]:
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail}
        )

    return exception_handler
