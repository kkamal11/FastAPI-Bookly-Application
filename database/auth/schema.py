from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List

from database.books.schema import Book
from database.reviews.schema import ReviewModel

class UserCreateModel(BaseModel):
    username: str = Field(min_length=3, max_length=8)
    email: str = Field(min_length=6)
    password: str
    first_name: str = Field(min_length=4, max_length=25)
    last_name: str = Field(min_length=4, max_length=25)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str = Field(min_length=6)
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserWithBooksModel(UserModel):
    books: List[Book]

class UserBookReviewModel(UserWithBooksModel):
    books: List[Book]
    reviews: List[ReviewModel]


class UserLoginModel(BaseModel):
    email: str = Field(min_length=6)
    password: str