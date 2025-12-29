from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

from datetime import datetime
import uuid 


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    first_name: str
    last_name: str
    password_hash: str = Field(exclude=True)
    is_verified: bool = Field(default=False)
    created_at : datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))
    updated_at : datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.utcnow
    ))


    def __repr__(self) -> str:
        return f"<User[username={self.username}, email={self.email}]>"