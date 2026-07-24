# app/models/response.py
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    detail: Optional[str] = None