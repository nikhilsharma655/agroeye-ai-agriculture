from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Consistent success envelope used by every AgroEye endpoint."""
    success: bool = True
    message: str
    data: Optional[T] = None


class ApiError(BaseModel):
    success: bool = False
    message: str
    error: str
