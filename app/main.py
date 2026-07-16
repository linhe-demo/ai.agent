# app/main.py
import sys
import io
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import invoice

# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 验证配置
settings.validate()

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="发票识别服务 - 支持批量识别，自动区分普票和专票",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    invoice.router,
    prefix=settings.API_V1_STR,
    tags=["发票识别"]
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_STR
    }


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} 启动成功")
    logger.info(f"API 文档地址: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"支持的格式: {settings.ALLOWED_EXTENSIONS}")
    logger.info(f"最大并发数: {settings.OCR_MAX_WORKERS}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info(f"{settings.PROJECT_NAME} 正在关闭...")