from fastapi import status, APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from database.main import get_session
from .service import AuthService
from database.auth.schema import UserCreateModel, RegisterUseEmailResponseModel, UserLoginModel, UserBookReviewModel, EmailModel
from .utils import create_access_token, verify_password, create_url_safe_token, decode_access_token, decode_url_safe_token
from config import env_config
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from database.redis import add_jti_to_blocklist
from src.error import (
    UserNotFoundError, InvalidCredentialsError, InsufficientPermissionsError, FailedInVerifyingUserError
)
from src.email.mail import EmailService

auth_router = APIRouter()
auth_service = AuthService()
email_service = EmailService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

@auth_router.post('/send-mail')
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome from Bookly</h1><p>This is a test email sent from the Bookly application.</p>"
    message = email_service.create_message(emails, "Welcome to Bookly", html)
    await email_service.mail.send_message(message)
    return {"message": "Emails sent successfully."}


@auth_router.post('/register', response_model=RegisterUseEmailResponseModel, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session)
):
    user = await auth_service.register_user(user_data, session)
    message = "User registered successfully. Please check your email to verify your account."
    if user:
        email_sent = True
        try:
            token_data = create_url_safe_token({"email": user.email})
            await email_service.send_html_mail_to_user_email(
                email=user.email,
                subject="Verify your Bookly account",
                html_template_data={
                    "user_name": user.username,
                    "verification_link": f"{env_config.FRONTEND_URL}/api/v1/auth/verify-email?token={token_data}",
                    "current_year": str(datetime.now().year),
                    "expiry_time": "10 minutes"
                },
                html_template_name="verify_account.html"
            )
        except Exception as e:
            email_sent = False
        if not email_sent:
            message = "User registered successfully, but we could not send a verification email. Please verify your email address or request a resend."
    return {
        "message": message,
        "user":user
    }

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

@auth_router.get('/verify-email', status_code=status.HTTP_200_OK)
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    try:
        token_data = decode_url_safe_token(token)
        email = token_data.get("email")
        user = None
        if email:
            user = await auth_service.get_user_by_email(email, session)
        if user is None:
            raise UserNotFoundError()
        if user.is_verified:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Email is already verified."
                }
            )
        user_data = {
            "email": user.email,
            "is_verified": True
        }
        updated_user = await auth_service.update_user_data(user_data, session)
        if not updated_user.is_verified:
            raise FailedInVerifyingUserError()
        try:
            await email_service.send_html_mail_to_user_email(
                email=user.email,
                subject="Account is Verified - Bookly",
                html_template_data={
                    "user_name": user.username,
                    "login_url": f"{env_config.FRONTEND_URL}/api/v1/auth/login",
                    "current_year": str(datetime.now().year),
                },
                html_template_name="verified_acc_success.html"
            )   
        except Exception as e:
                pass
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Email verified successfully."
            }
        )
    except Exception as e:
        raise FailedInVerifyingUserError()


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