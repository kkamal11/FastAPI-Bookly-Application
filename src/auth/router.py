from fastapi import status, APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from typing import List
import uuid

from database.main import get_session
from .service import AuthService
from database.auth.schema import UserCreateModel, UserModel, UserLoginModel, UserBookReviewModel, EmailModel
from .utils import create_access_token, verify_password
from config import env_config
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from database.redis import add_jti_to_blocklist
from src.error import (
    UserNotFoundError, InvalidCredentialsError, InsufficientPermissionsError
)
from src.email.mail import mail, create_message

auth_router = APIRouter()
auth_service = AuthService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

@auth_router.post('/send-mail')
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome from Bookly</h1><p>This is a test email sent from the Bookly application.</p>"
    message = create_message(emails, "Welcome to Bookly", html)
    await mail.send_message(message)
    return {"message": "Emails sent successfully."}


@auth_router.post('/register', response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session)
):
    user = await auth_service.register_user(user_data, session)
    return user

@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(
    user_login_data : UserLoginModel, 
    session: AsyncSession = Depends(get_session)
):
    email = user_login_data.email
    password = user_login_data.password

    user = await auth_service.get_user_by_email(email, session)

    if not user:
        raise UserNotFoundError()
    
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    
    try:
        access_token = create_access_token(
            user_data={
                "user_uid": str(user.uid),
                "email": user.email,
                "role": user.role,
            }
        )

        refresh_token = create_access_token(
            user_data={
                "user_uid": str(user.uid),
                "email": user.email,
            },
            refresh=True,
            expiry=env_config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "refresh_token": refresh_token,
                "message": "Login successful.",
                "user":{
                    "email": user.email,
                    "uid": str(user.uid),
                }
            }
        )
    except Exception as e:
        raise InsufficientPermissionsError()


@auth_router.get('/refresh-token', status_code=status.HTTP_200_OK)
async def get_new_access_token(token_details :dict = Depends(RefreshTokenBearer())):
    try:
        expiry_timestamp = token_details.get("exp")
        if datetime.fromtimestamp(expiry_timestamp) > datetime.utcnow():
            new_access_token = create_access_token(
                user_data=token_details['user']
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "access_token": new_access_token,
                    "token_type": "bearer",
                    "message": "New access token generated successfully."
                }
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{str(e)[:100]}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{str(e)[:100]}")


@auth_router.get('/me', response_model=UserBookReviewModel, status_code=status.HTTP_200_OK)
async def get_current_user(
        user = Depends(get_current_user), 
        _:bool = Depends(role_checker)
    ):
    return user


@auth_router.post('/logout', status_code=status.HTTP_200_OK)
async def logout_user(
    token_details :dict = Depends(AccessTokenBearer()),
):
    try:
        jti = token_details.get("jti")
        await add_jti_to_blocklist(jti)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Logout successful. Token has been revoked."
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{str(e)[:100]}")