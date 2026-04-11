from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str

class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=120)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)  

class Token(BaseModel):
    access_token: str
    token_type: str
      
class ShowBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    watch_status: str | None = Field(default="Want to Watch", max_length=100)
    completeness: str | None = Field(default="On Going", max_length=100)
    review: str = Field(min_length=1)

class ShowCreate(ShowBase):
    pass

class ShowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    watch_status: str | None = Field(default=None, max_length=100)
    completeness: str | None = Field(default=None, max_length=100)
    review: str | None = Field(default=None, min_length=1)

class ShowResponse(ShowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic
