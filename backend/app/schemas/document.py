
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(default="General", max_length=100)


class DocumentResponse(BaseModel):
    id: int
    name: str
    category: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
