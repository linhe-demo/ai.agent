import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件路径（按日期命名）
LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
ERROR_LOG_FILE = LOG_DIR / f"error_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logging():
    """配置日志系统"""

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除已有的处理器（避免重复）
    logger.handlers.clear()

    # 1. 控制台处理器（输出到终端）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 2. 文件处理器（所有日志）
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # 保留5个备份
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 3. 错误日志单独文件
    error_file_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    error_file_handler.setFormatter(error_formatter)
    logger.addHandler(error_file_handler)

    return logger


# 获取日志记录器
def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    if name:
        return logging.getLogger(name)
    return logging.getLogger()