from fastapi import FastAPI, status
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

class UsernameAlreadyTakenError(BooklyException):
    """Exception raised when attempting to create a user with a username that is already taken."""
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

class InternalServerError(BooklyException):
    """Exception raised for internal server errors."""
    pass

def create_exception_handler(status_code: int, detail: Any) -> Callable[[Request, Exception],JSONResponse]:
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail}
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExistsError, 
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "User with this email already exists.",
                "error_code": "USER_ALREADY_EXISTS",
                "resolution": "Please use a different email."
            }
        )
    )
    app.add_exception_handler(
        UsernameAlreadyTakenError, 
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Username is already taken.",
                "error_code": "USERNAME_ALREADY_TAKEN",
                "resolution": "Please use a different username."
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentialsError, 
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid email or password.",
                "error_code": "INVALID_CREDENTIALS",
                "resolution": "Please check your credentials and try again."
            }
        )
    )
    app.add_exception_handler(
        InvalidTokenError, 
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "The provided token is invalid.",
                "error_code": "INVALID_TOKEN",
                "resolution": "Please provide a valid token."
            }
        )
    )
    app.add_exception_handler(
        UserNotFoundError, 
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User not found.",
                "error_code": "USER_NOT_FOUND",
                "resolution": "Please check the user details and try again."
            }
        )
    )
    app.add_exception_handler(
        InsufficientPermissionsError, 
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "You do not have sufficient permissions to perform this action.",
                "error_code": "INSUFFICIENT_PERMISSIONS",
                "resolution": "Please contact the administrator if you believe this is an error."
            }
        )
    )


def register_internal_server_error_handler(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def internal_server_error_handler(
        request: Request,
        exc: Exception,
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={ 
                    "message": "An unexpected error occurred on the server.",
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "resolution": "Please try again later or contact support if the issue persists."
            }
        )