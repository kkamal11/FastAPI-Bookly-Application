from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi.exceptions import HTTPException
from fastapi import status
from database.auth.models import User
from database.auth.schema import UserCreateModel
from .utils import generate_password_hash, verify_password


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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User with this email already exists.")
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
