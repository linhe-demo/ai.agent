# app/services/invoice_service.py
import time
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import HTTPException

from app.core.config import settings
from app.services.ocr_service import ocr_service
from app.services.deepseek_service import deepseek_service
from app.models.invoice import InvoiceResult, InvoiceData, InvoiceMetadata

logger = logging.getLogger(__name__)


class InvoiceService:
    """发票处理服务"""

    def __init__(self):
        self.max_workers = settings.OCR_MAX_WORKERS

    def process_single(
            self,
            file_bytes: bytes,
            filename: str,
            index: int
    ) -> InvoiceResult:
        """处理单张发票"""
        start_time = time.time()

        try:
            # 1. OCR 识别
            ocr_text = ocr_service.extract_text(file_bytes, filename)

            if not ocr_text or not ocr_text.strip():
                return InvoiceResult(
                    index=index,
                    filename=filename,
                    status="failed",
                    error="未从文件中提取到文字内容"
                )

            # 2. 预先判断发票类型
            pre_type = deepseek_service.classify_invoice_type(ocr_text)

            # 3. 调用 DeepSeek 解析
            result_data = deepseek_service.parse_invoice(ocr_text)

            # 4. 构建元数据
            processing_time = time.time() - start_time

            metadata = InvoiceMetadata(
                filename=filename,
                file_type=filename.lower().split(".")[-1],
                index=index,
                ocr_text_preview=ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text,
                pre_classified_type=pre_type,
                processing_time=round(processing_time, 2)
            )

            # 5. 构建发票数据
            invoice_data = InvoiceData(**result_data)
            invoice_data.metadata = metadata

            return InvoiceResult(
                index=index,
                filename=filename,
                status="success",
                data=invoice_data
            )

        except HTTPException as e:
            return InvoiceResult(
                index=index,
                filename=filename,
                status="failed",
                error=e.detail
            )
        except Exception as e:
            logger.error(f"处理发票 {filename} 失败: {e}")
            return InvoiceResult(
                index=index,
                filename=filename,
                status="failed",
                error=str(e)
            )

    def process_batch(
            self,
            file_items: List[Dict[str, Any]]
    ) -> List[InvoiceResult]:
        """批量处理发票"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(
                    self.process_single,
                    item["content"],
                    item["filename"],
                    item["index"]
                ): item for item in file_items
            }

            # 收集结果
            for future in as_completed(future_to_file):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    item = future_to_file[future]
                    logger.error(f"处理文件 {item['filename']} 时发生异常: {e}")
                    results.append(
                        InvoiceResult(
                            index=item["index"],
                            filename=item["filename"],
                            status="failed",
                            error=str(e)
                        )
                    )

        # 按原始顺序排序
        results.sort(key=lambda x: x.index)
        return results


# 创建全局发票处理服务实例
invoice_service = InvoiceService()