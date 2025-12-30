from fastapi import status, APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
import uuid

from database.books.schema import Book, BookUpdateModel, BookCreateModel, BookDetailWithReviewsModel
from database.main import get_session
from .service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.error import InsufficientPermissionsError, BookNotFoundError

book_router = APIRouter()
books_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))

@book_router.get("/", response_model=List[BookDetailWithReviewsModel],  dependencies=[role_checker])
async def get_all_books(
    session:AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    # _:bool = Depends(role_checker)
    ) -> List[Book]:
    books = await books_service.get_all_books(session)
    return books

@book_router.get('/user/{user_id}', response_model=List[BookDetailWithReviewsModel],  dependencies=[role_checker])
async def get_user_books(
    user_id:str,
    session:AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    # _:bool = Depends(role_checker)
    ) -> List[Book]:
    u_id = token_details['user']['user_uid']
    if user_id != u_id:
        raise InsufficientPermissionsError()
    books = await books_service.get_user_books(session, user_id)
    return books

@book_router.get("/{book_id}", response_model=BookDetailWithReviewsModel, dependencies=[role_checker])
async def get_book(
    book_id: uuid.UUID,
    session:AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)) -> Book:
    book = await books_service.get_book_by_id(session, book_id)
    if not book:
        raise BookNotFoundError()
    return book

@book_router.post("/",status_code=status.HTTP_201_CREATED, response_model=BookDetailWithReviewsModel, dependencies=[role_checker])
async def add_book(
    book_data: BookCreateModel, 
    session:AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)) -> Book:
    user_uid = token_details['user']['user_uid']
    new_book = await books_service.create_book(session, book_data, user_uid)
    return new_book

@book_router.patch("/{book_id}",status_code=status.HTTP_404_NOT_FOUND, response_model=BookDetailWithReviewsModel, dependencies=[role_checker])
async def update_book(
    book_id: uuid.UUID, updated_book: BookUpdateModel, 
    session:AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer))-> Book:
    book = await books_service.update_book(session, book_id, updated_book)
    if book:
        return book
    raise BookNotFoundError()

@book_router.delete("/{book_id}",status_code=status.HTTP_404_NOT_FOUND, dependencies=[role_checker])
async def delete_book(
    book_id: uuid.UUID, 
    session:AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)) -> dict:
    book = await books_service.delete_book(session, book_id)
    if book:
        return {"message": f"Book {book.title} deleted successfully"}
    raise BookNotFoundError()
