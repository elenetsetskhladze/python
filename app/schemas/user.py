import datetime
from pydantic import BaseModel, EmailStr, Field



class UserCreate(BaseModel):
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    registered_at: datetime.datetime
    role: str


class UserLogin(BaseModel):
    username: str
    password: str