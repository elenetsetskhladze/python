from pydantic import BaseModel, Field
import datetime


class ReviewCreate(BaseModel):
    rating: float = Field(ge=1, le=10)
    comments: str


class ReviewResponse(BaseModel):
    id: int
    rating: float
    comments: str
    user_id: int
    product_id: int
    created_at: datetime.datetime