from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from typing import Optional
import uuid 

class Reviews(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    rating: int = Field(lt=5, gt=0)
    review_text: str
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid"
    )
    book_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="books.uid"
    )
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Books"] = Relationship(back_populates="reviews")


    def __repr__(self) -> str:
        return f"<Review[Rating={self.rating}, reviewer={self.user.username if self.user else None}]>"
    

