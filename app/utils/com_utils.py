import base64
import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)

def decode_base64_content(encoded_content: str) -> str:
    """
    解码 Base64 内容
    """
    try:
        # Base64 解码
        decoded_bytes = base64.b64decode(encoded_content)
        # 转为 UTF-8 字符串
        decoded_text = decoded_bytes.decode("utf-8")
        return decoded_text
    except Exception as e:
        logger.error(f"Base64 解码失败: {e}")
        raise HTTPException(status_code=400, detail="聊天内容 Base64 解码失败，请确认编码格式正确")


def text_to_base64(text: str, encoding: str = "utf-8") -> str:
    """
    将文本转换为 Base64，支持多种编码

    Args:
        text: 要编码的文本
        encoding: 编码格式，支持 "utf-8", "gbk", "gb2312" 等

    Returns:
        Base64 编码后的字符串
    """
    # 如果是中文且未指定编码，默认使用 UTF-8
    if encoding == "utf-8":
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")
    else:
        return base64.b64encode(text.encode(encoding)).decode("utf-8")


