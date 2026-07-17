# app/main.py
import os
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
ENV = os.getenv("ENV", "dev")  # 如果不设置ENV，默认就是dev
env_name = ""

# 根据环境决定是否开启文档
if ENV == "production":
    # 生产环境：关闭所有文档
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI智能体-综合服务",
        docs_url=None,        # 关闭 /docs
        redoc_url=None,       # 关闭 /redoc
        openapi_url=None      # 关闭 /openapi.json（这个一定要关！）
    )
    env_name = "正式环境"
else:
    # 开发/测试环境：正常开启文档
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI智能体-综合服务",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    env_name = "测试环境"



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
    logger.info(f"当前环境 {env_name}")
    logger.info(f"API 文档地址: http://{settings.HOST}:{settings.PORT}/docs 注意正式环境已关闭文档功能，只能在测试服查阅")
    logger.info(f"支持的格式: {settings.ALLOWED_EXTENSIONS}")
    logger.info(f"最大并发数: {settings.OCR_MAX_WORKERS}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info(f"{settings.PROJECT_NAME} 正在关闭...")