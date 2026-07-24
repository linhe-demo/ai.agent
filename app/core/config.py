# app/core/config.py
import os
from dotenv import load_dotenv
from typing import Set

# 加载环境变量
load_dotenv()


class Settings:
    """应用配置类"""

    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_TIMEOUT: int = int(os.getenv("DEEPSEEK_TIMEOUT", "30"))
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.1"))

    # Coze 配置
    COZE_API_KEY: str = os.getenv("COZE_API_KEY", "")
    COZE_API_URL: str = os.getenv("COZE_API_URL", "")
    COZE_MODEL_ID: str = os.getenv("COZE_MODEL_ID", "")

    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # OCR 配置
    OCR_LANG: str = os.getenv("OCR_LANG", "ch")
    OCR_MAX_WORKERS: int = int(os.getenv("OCR_MAX_WORKERS", "3"))
    OCR_USE_GPU: bool = os.getenv("OCR_USE_GPU", "False").lower() == "true"

    # 文件限制
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10485760))
    MAX_FILES: int = int(os.getenv("MAX_FILES", 20))
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,bmp,tiff,pdf")

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    #REDIS 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1" )
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 6))
    REDIS_PASSWORD: str = int(os.getenv("REDIS_PASSWORD", ""))
    REDIS_RULE_KEY: str = os.getenv("REDIS_RULE_KEY", "AI:SERVICE:")

    #CRM 配置
    CRM_ZY_URL: str = os.getenv("CRM_ZY_URL", "")
    CRM_ZY_AUTHORIZATION: str = os.getenv("CRM_ZY_AUTHORIZATION", "")

    # API 配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AI智能体服务"
    VERSION: str = "2.0.0"

    @property
    def allowed_extensions_set(self) -> Set[str]:
        """获取允许的文件扩展名集合"""
        return set(self.ALLOWED_EXTENSIONS.split(","))

    def is_allowed_file(self, filename: str) -> bool:
        """检查文件是否允许上传"""
        ext = filename.lower().split(".")[-1]
        return ext in self.allowed_extensions_set

    def validate(self) -> bool:
        """验证必要的配置是否存在"""
        if not self.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置，请在 .env 文件中配置")
        return True


# 创建全局配置实例
settings = Settings()