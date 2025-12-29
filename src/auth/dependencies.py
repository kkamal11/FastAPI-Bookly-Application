from fastapi import Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
import logging

from .utils import decode_access_token
from database.redis import is_jti_in_blocklist

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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization credentials"
            )
        
        if creds.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )

        token = creds.credentials 
        token_data = self.is_token_valid(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization token is expired or invalid.")
        
        if await is_jti_in_blocklist(token_data['jti']):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error":"Token has been revoked.",
                "resolution":"Please login again to obtain a new token."
            })

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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid access token, not a refresh token.")


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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please provide a valid refresh token, not an access token.")