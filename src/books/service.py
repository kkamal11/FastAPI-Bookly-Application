from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from typing import List
import uuid
from datetime import datetime

from database.books.schema import BookCreateModel, BookUpdateModel, Book
from database.books.models import Books

class BookService:
    async def get_all_books(self, session: AsyncSession) -> List[Book]:
        query = select(Books).order_by(desc(Books.created_at))
        result = await session.execute(query)
        books = result.scalars().all()
        return books
    
    async def get_book_by_id(self, session: AsyncSession, book_id: uuid.UUID) -> Book | None: 
        query = select(Books).where(Books.uid == book_id)
        result = await session.execute(query)
        book = result.scalar_one_or_none()
        return book

    async def create_book(self, session: AsyncSession, book_data: BookCreateModel) -> Book:
        book_data_dict = book_data.model_dump()
        new_book = Books(**book_data_dict)
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_book(self, session: AsyncSession, book_id: uuid.UUID, book_data: BookUpdateModel) -> Book | None:
        book_to_update = await self.get_book_by_id(session, book_id)  
        if book_to_update:
            updated_book_data = book_data.model_dump()
            for key, value in updated_book_data.items():
                setattr(book_to_update, key, value) 
            await session.commit()
            await session.refresh(book_to_update)
        return book_to_update

    async def delete_book(self, session: AsyncSession, book_id: uuid.UUID) -> Book | None:
        book_to_delete = await self.get_book_by_id(session, book_id)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
        return book_to_delete

    