# app/services/deepseek_service.py
import json
import re
import logging
import requests
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekService:
    """DeepSeek API 服务"""

    # 发票提取提示词模板
    EXTRACTION_PROMPT = """
你是一个专业的发票信息提取专家。请从以下OCR识别的发票文本中，提取关键信息并以JSON格式返回。

**第一步：判断发票类型**
首先判断这是增值税专用发票还是增值税普通发票，判断依据：
- 专票特征：标题包含"增值税专用发票"，通常有"购买方"和"销售方"两栏
- 普票特征：标题包含"增值税普通发票"或"普通发票"

**提取字段**：
1. 发票类型 (invoice_type) - 必须是以下值之一：["增值税专用发票", "增值税普通发票", "其他"]
2. 发票代码 (invoice_code)
3. 发票号码 (invoice_number)
4. 开票日期 (invoice_date) - 格式：YYYY-MM-DD
5. 购买方名称 (buyer_name)
6. 购买方纳税人识别号 (buyer_tax_id)
7. 购买方地址电话 (buyer_address_phone) - 可选
8. 购买方开户行及账号 (buyer_bank_account) - 可选
9. 销售方名称 (seller_name)
10. 销售方纳税人识别号 (seller_tax_id)
11. 销售方地址电话 (seller_address_phone) - 可选
12. 销售方开户行及账号 (seller_bank_account) - 可选
13. 总金额（不含税）(total_amount) - 保留两位小数
14. 税率 (tax_rate) - 如：13%、6%等
15. 税额 (tax_amount) - 保留两位小数
16. 价税合计 (total_amount_with_tax) - 保留两位小数
17. 货物或应税劳务名称 (goods_name) - 主要商品名称

OCR识别文本如下：
{ocr_text}

请只返回JSON格式的结果，不要包含其他说明文字。如果某个字段找不到，请返回null。
"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.model = settings.DEEPSEEK_MODEL
        self.timeout = settings.DEEPSEEK_TIMEOUT
        self.temperature = settings.DEEPSEEK_TEMPERATURE

        if not self.api_key:
            raise ValueError("DeepSeek API Key 未设置")

    def parse_invoice(self, ocr_text: str) -> dict:
        """调用 DeepSeek API 解析发票信息"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt = self.EXTRACTION_PROMPT.format(ocr_text=ocr_text)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的发票信息提取专家，擅长从发票文本中提取结构化数据并准确区分发票类型。"
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # 解析 JSON
            try:
                parsed_json = json.loads(content)
                return parsed_json
            except json.JSONDecodeError:
                # 尝试提取 JSON
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="DeepSeek返回的内容无法解析为JSON"
                    )

        except requests.exceptions.RequestException as e:
            logger.error(f"调用 DeepSeek API 失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"调用DeepSeek API失败: {str(e)}"
            )

    @staticmethod
    def classify_invoice_type(ocr_text: str) -> str:
        """预先判断发票类型（快速分类）"""
        special_keywords = ["增值税专用发票", "专用发票", "增值税专票"]
        normal_keywords = ["增值税普通发票", "普通发票", "增值税普票", "电子普通发票"]

        for kw in special_keywords:
            if kw in ocr_text:
                return "增值税专用发票"

        for kw in normal_keywords:
            if kw in ocr_text:
                return "增值税普通发票"

        return "未知"


# 创建全局 DeepSeek 服务实例
deepseek_service = DeepSeekService()