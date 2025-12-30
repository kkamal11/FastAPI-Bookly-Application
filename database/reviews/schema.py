from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(lt=6, gt=0)
    review_text: str
    user_uid: uuid.UUID
    book_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=6, gt=0)
    review_text: str

class ReviewUpdateModel(BaseModel):
    rating: int = Field(lt=6, gt=0)
    review_text: str