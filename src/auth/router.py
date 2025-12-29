from fastapi import status, APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from typing import List
import uuid

from database.main import get_session
from .service import AuthService
from database.auth.schema import UserCreateModel, UserModel, UserLoginModel
from .utils import create_access_token, decode_access_token, verify_password
from config import env_config
from .dependencies import RefreshTokenBearer, AccessTokenBearer
from database.redis import add_jti_to_blocklist

auth_router = APIRouter()
auth_service = AuthService()

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    
    try:
        access_token = create_access_token(
            user_data={
                "user_uid": str(user.uid),
                "email": user.email,
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"{str(e)[:100]}")


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