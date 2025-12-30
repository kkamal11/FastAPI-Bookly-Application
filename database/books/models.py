from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from typing import Optional
import uuid 

from database.auth import models

class Books(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    title: str
    author: str
    published_date: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    publisher: str
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid"
    )
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    user: Optional["models.User"] = Relationship(back_populates="books")


    def __repr__(self) -> str:
        return f"<Book[title={self.title}, author={self.author}]>"