
from pydantic import BaseModel, Field


class PermissionCreate(BaseModel):
    user_id: int = Field(gt=0)
    can_read: bool = False
    can_edit: bool = False
    can_delete: bool = False


class PermissionResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    can_read: bool
    can_edit: bool
    can_delete: bool
    granted_by: int
