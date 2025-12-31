from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
import logging
from typing import List

from .utils import decode_access_token
from database.redis import is_jti_in_blocklist
from database.main import get_session
from .service import AuthService
from database.auth.models import User
from src.error import InvalidTokenError, RevokedTokenError, InvalidCredentialsError,\
    AccessTokenRequiredError, RefreshTokenRequiredError, UserNotFoundError, InsufficientPermissionsError,\
    UserAccountNotVerifiedError

user_service = AuthService()

class TokenBearer(HTTPBearer):
    """
    Custom HTTP Bearer class for access token authentication.
    Inherits from FastAPI's HTTPBearer to handle bearer token extraction.
    """
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request:Request) -> HTTPAuthorizationCredentials | None:
        creds =  await super().__call__(request)
        # print(creds.scheme)
        # print(creds.credentials)
        if not creds:
            raise InvalidCredentialsError()
        
        if creds.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )

        token = creds.credentials 
        token_data = self.is_token_valid(token)
        if not token_data:
            raise InvalidTokenError()
        
        if await is_jti_in_blocklist(token_data['jti']):
            raise RevokedTokenError()

        self.verify_token_data(token_data)

        return token_data
    
    def is_token_valid(self, token: str) -> bool | None:
        """
        Validates the provided access token and returns the token data if valid.
        """
        try:
            token_data = decode_access_token(token)
            if token_data:
                return token_data
            return None
        except Exception as e:
            logging.exception(e)
            return None
    
    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Subclasses must implement this method.")
        
class AccessTokenBearer(TokenBearer):
    """
    Dependency class for access token authentication.
    Inherits from TokenBearer to utilize token validation logic.
    """
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def verify_token_data(self, token_data: dict) -> bool:
        """
        Verifies the token data to ensure it contains required fields.
        """
        if token_data and token_data['refresh']:
            raise AccessTokenRequiredError()


class RefreshTokenBearer(TokenBearer):
    """
    Dependency class for refresh token authentication.
    Inherits from TokenBearer to utilize token validation logic.
    """
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def verify_token_data(self, token_data: dict) -> bool:
        """
        Verifies the token data to ensure it contains required fields.
        """
        if token_data and not token_data['refresh']:
            raise RefreshTokenRequiredError()

async def get_current_user(
        token_details: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session)) -> dict:
    """
    Dependency function to retrieve the current user from the token data.
    """
    email = token_details['user']['email']
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise UserNotFoundError()
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> None:
        if not current_user.is_verified:
            raise UserAccountNotVerifiedError()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermissionsError()

