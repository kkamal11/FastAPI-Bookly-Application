from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from fastapi import status
from database.auth.models import User
from database.auth.schema import UserCreateModel
from .utils import generate_password_hash, verify_password
from src.error import UserAlreadyExistsError, UsernameAlreadyTakenError, UserNotFoundError
from logger.user_logger import get_user_logger

class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        return user
    
    async def check_user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def register_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict['password'])
        new_user.role = "user"
        user_exists = await self.check_user_exists(user_data_dict["email"], session)
        if user_exists:
            raise UserAlreadyExistsError()
        try:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await session.rollback()
            msg = str(e.orig)
            if "ix_users_username" in msg:
                raise UsernameAlreadyTakenError();
        except Exception as e:
            await session.rollback()
            raise e
    
    async def update_user_data(self, user_data, session: AsyncSession) -> User | None:
        email = user_data.get("email")
        user = await self.get_user_by_email(email, session)
        if not user:
            raise UserNotFoundError()
        for key, value in user_data.items():
            if key == "email":
                continue
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user
        
