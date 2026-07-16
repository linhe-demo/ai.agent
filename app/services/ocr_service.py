# app/services/ocr_service.py
import io
import logging
from typing import Optional
from PIL import Image
from paddleocr import PaddleOCR
import PyPDF2
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class OCRService:
    """OCR 识别服务"""

    def __init__(self, lang: str = 'ch'):
        """初始化 OCR 服务"""
        try:
            self.ocr = PaddleOCR(lang=lang)
        except Exception as e:
            logger.warning(f"PaddleOCR 初始化失败: {e}")
            self.ocr = PaddleOCR(use_textline_orientation=True, lang=lang)
        self.lang = lang

    def extract_from_image(self, image_bytes: bytes) -> str:
        """从图片中提取文字"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            result = self.ocr.ocr(image, cls=True)

            text_lines = []
            if result and len(result) > 0:
                for line in result:
                    if line:
                        for word_info in line:
                            if len(word_info) >= 2:
                                text_lines.append(word_info[1][0])

            if not text_lines:
                raise HTTPException(status_code=400, detail="未从图片中识别到文字")

            return "\n".join(text_lines)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"图片 OCR 识别失败: {e}")
            raise HTTPException(status_code=400, detail=f"图片OCR识别失败: {str(e)}")

    def extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """从 PDF 中提取文字"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PyPDF2.PdfReader(pdf_file)

            text_pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    text_pages.append(text.strip())

            if not text_pages:
                raise HTTPException(status_code=400, detail="PDF中未提取到文字内容")

            return "\n".join(text_pages)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"PDF 解析失败: {e}")
            raise HTTPException(status_code=400, detail=f"PDF解析失败: {str(e)}")

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """根据文件类型提取文字"""
        ext = filename.lower().split('.')[-1]

        if ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            return self.extract_from_image(file_bytes)
        elif ext == 'pdf':
            return self.extract_from_pdf(file_bytes)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")


# 创建全局 OCR 服务实例
ocr_service = OCRService()