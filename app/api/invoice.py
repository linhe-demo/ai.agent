# app/api/invoice.py
import time
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.invoice_service import invoice_service
from app.models.invoice import (
    InvoiceResult,
    InvoiceSummary,
    BatchInvoiceResponse,
    InvoiceClassification,
    InvoiceData
)
from app.models.response import ResponseModel
from app.utils.file_utils import validate_file_extension, validate_file_size

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "AI-AGENT"}


@router.post("/invoice/extract")
async def extract_single_invoice(
        file: UploadFile = File(..., description="发票文件（图片或PDF）")
):
    """
    单张发票识别（兼容旧版）

    支持格式：jpg, jpeg, png, bmp, tiff, pdf
    """
    # 验证文件
    content = await file.read()
    validate_file_size(content, settings.MAX_FILE_SIZE)
    validate_file_extension(file.filename, settings.allowed_extensions_set)

    # 处理
    result = invoice_service.process_single(content, file.filename, 0)

    if result.status == "failed":
        raise HTTPException(status_code=400, detail=result.error)

    return JSONResponse(
        status_code=200,
        content={
            "code": 0,
            "message": "识别成功",
            "data": result.data.model_dump() if result.data else None
        }
    )


@router.post("/invoice/extract_with_classification")
async def extract_invoice_with_classification(
        file: UploadFile = File(..., description="发票文件（图片或PDF）")
):
    """
    单张发票识别（含分类信息）

    自动区分增值税专用发票和普通发票
    """
    # 验证文件
    content = await file.read()
    validate_file_size(content, settings.MAX_FILE_SIZE)
    validate_file_extension(file.filename, settings.allowed_extensions_set)

    # 处理
    result = invoice_service.process_single(content, file.filename, 0)

    if result.status == "failed":
        raise HTTPException(status_code=400, detail=result.error)

    # 提取发票类型
    invoice_data = result.data
    invoice_type = invoice_data.invoice_type or "未知" if invoice_data else "未知"

    classification = InvoiceClassification(
        type=invoice_type,
        is_special="专用" in invoice_type,
        is_normal="普通" in invoice_type,
        description=(
            "增值税专用发票" if "专用" in invoice_type else
            "增值税普通发票" if "普通" in invoice_type else
            "其他类型发票"
        )
    )

    return JSONResponse(
        status_code=200,
        content={
            "code": 0,
            "message": "识别成功",
            "classification": classification.model_dump(),
            "data": invoice_data.model_dump() if invoice_data else None
        }
    )


@router.post("/invoice/batch_extract")
async def batch_extract_invoices(
        files: List[UploadFile] = File(..., description="批量上传发票文件"),
        max_concurrent: int = Form(settings.OCR_MAX_WORKERS, description="最大并发数")
):
    """
    批量发票识别接口

    支持同时上传多张图片或PDF，自动区分普票和专票
    """
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件")

    if len(files) > settings.MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"单次最多支持 {settings.MAX_FILES} 个文件"
        )

    # 验证并读取文件
    file_items = []
    for idx, file in enumerate(files):
        # 验证文件扩展名
        validate_file_extension(file.filename, settings.allowed_extensions_set)

        # 读取文件内容
        content = await file.read()
        validate_file_size(content, settings.MAX_FILE_SIZE)

        file_items.append({
            "filename": file.filename,
            "content": content,
            "index": idx
        })

    # 批量处理
    results = invoice_service.process_batch(file_items)

    # 统计信息
    success_count = sum(1 for r in results if r.status == "success")
    failed_count = len(results) - success_count

    special_count = 0
    normal_count = 0
    unknown_count = 0

    for r in results:
        if r.status == "success" and r.data:
            invoice_type = r.data.invoice_type or "未知"
            if "专用" in invoice_type:
                special_count += 1
            elif "普通" in invoice_type:
                normal_count += 1
            else:
                unknown_count += 1

    summary = InvoiceSummary(
        total=len(results),
        success=success_count,
        failed=failed_count,
        special_invoice_count=special_count,
        normal_invoice_count=normal_count,
        unknown_invoice_count=unknown_count
    )

    # 构建响应
    response_data = BatchInvoiceResponse(
        code=0,
        message=f"批量识别完成，成功 {success_count} 张，失败 {failed_count} 张",
        summary=summary,
        results=results
    )

    return JSONResponse(
        status_code=200,
        content=response_data.model_dump()
    )


@router.get("/invoice/stats")
async def get_invoice_stats():
    """
    获取发票识别统计信息（示例）

    实际生产环境可以从数据库获取
    """
    return {
        "code": 0,
        "message": "success",
        "data": {
            "service": "invoice-recognition",
            "supported_formats": list(settings.allowed_extensions_set),
            "max_file_size": settings.MAX_FILE_SIZE,
            "max_files": settings.MAX_FILES,
            "max_concurrent": settings.OCR_MAX_WORKERS,
            "version": settings.VERSION
        }
    }