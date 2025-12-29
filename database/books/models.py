from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

from datetime import datetime
import uuid 

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
    created_at : datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    updated_at : datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))


    def __repr__(self) -> str:
        return f"<Book[title={self.title}, author={self.author}]>"