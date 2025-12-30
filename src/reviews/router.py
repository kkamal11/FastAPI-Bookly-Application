from fastapi import status, APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
import uuid
import logging

from database.books.schema import Book, BookUpdateModel, BookCreateModel
from database.reviews.schema import ReviewModel, ReviewCreateModel, ReviewUpdateModel
from database.main import get_session
from .service import ReviewService
from src.auth.dependencies import get_current_user
from database.auth.models import User

review_router = APIRouter()
review_service = ReviewService()

@review_router.post('/book/{book_id}')
async def add_review_to_book(
    book_id: uuid.UUID,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        new_review = await review_service.add_review(
            user_email=current_user.email,
            book_id=book_id,
            review_data=review_data,
            session=session
        )
        return new_review
    except HTTPException as e:
        logging.error(f"HTTPException while adding review: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error while adding review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding the review1: {str(e)}"
        )