# app/utils/file_utils.py
import hashlib
from typing import Tuple
from fastapi import UploadFile, HTTPException


def validate_file_size(content: bytes, max_size: int) -> None:
    """验证文件大小"""
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过 {max_size // 1024 // 1024}MB 限制"
        )


def validate_file_extension(filename: str, allowed_extensions: set) -> str:
    """验证文件扩展名"""
    ext = filename.lower().split('.')[-1]
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，支持的格式: {', '.join(allowed_extensions)}"
        )
    return ext


def calculate_file_md5(content: bytes) -> str:
    """计算文件 MD5"""
    return hashlib.md5(content).hexdigest()


def get_file_size_str(size: int) -> str:
    """获取文件大小可读字符串"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"