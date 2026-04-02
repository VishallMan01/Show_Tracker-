from pydantic import BaseModel, ConfigDict, Field

class ShowBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    watch_status: str = Field(min_length=1, max_length=100)
    completeness: str = Field(min_length=1, max_length=100)
    review: str = Field(min_length=1, max_length=100)

class ShowCreate(ShowBase):
    pass

class ShowResponse(ShowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
