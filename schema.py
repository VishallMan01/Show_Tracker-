from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str

class ShowBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    watch_status: str = Field(min_length=1, max_length=100)
    completeness: str = Field(min_length=1, max_length=100)
    review: str = Field(min_length=1, max_length=100)

class ShowCreate(ShowBase):
    user_id: int

class ShowResponse(ShowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: int
    date_posted: datetime
    author: UserResponse
