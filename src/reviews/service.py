from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from typing import List
import uuid
from datetime import datetime

from database.reviews.models import Reviews
from database.reviews.schema import ReviewCreateModel, ReviewUpdateModel, ReviewModel
from src.auth.service import AuthService
from src.books.service import BookService
from src.error import UserNotFoundError, BookNotFoundError

user_service = AuthService()
book_service = BookService()

class ReviewService:

    async def add_review(self, user_email: str, 
                         book_id: uuid.UUID,
                         review_data: ReviewCreateModel,
                         session: AsyncSession
        ) -> ReviewModel:
        try:
            user = await user_service.get_user_by_email(session=session, email=user_email)
            if not user:
                raise UserNotFoundError()

            book = await book_service.get_book_by_id(session=session, book_id=book_id)
            if not book:
                raise BookNotFoundError()
            review_data_dict = review_data.model_dump()
            new_review = Reviews(**review_data_dict)
            new_review.user = user
            new_review.book = book
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while adding the review: {str(e)}"
            )