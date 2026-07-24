import json
import re
import logging
from typing import Dict
from fastapi import HTTPException
from openai import OpenAI
from volcenginesdkarkruntime import Ark

from app.prompt.chat.analysis import analysis
from app.prompt.chat.materials import materials
from app.prompt.chat.sample import sample
from app.core.config import settings


logger = logging.getLogger(__name__)


class Coze:
    """Coze API 服务"""

    def __init__(self):
        self.api_key = settings.COZE_API_KEY
        self.api_url = settings.COZE_API_URL
        self.model = settings.COZE_MODEL_ID
        self.ask_client = self.init_client()
        self.deep_client = self.init_deep_client()


        self.rules = None  # 内存缓存
        self._redis_enabled = True  # 是否启用 Redis

        self.deep_model = "deepseek-v4-flash"
        # deepseek-v4-flash

        if not self.api_key:
            raise ValueError("Coze API Key 未设置")

    def init_client(self):
        return Ark(
            base_url=self.api_url,
            api_key=self.api_key,
        )

    @staticmethod
    def init_deep_client():
        return OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,  # 你的 DeepSeek API Key
            base_url="https://api.deepseek.com"  # DeepSeek 官方 endpoint
        )



    def classify_with_deepseek(self, chat_content: str) -> dict:
        """使用 DeepSeek 进行分类"""

        # 构建提示词
        prompt = analysis.build_classification_prompt(chat_content)

        try:
            logger.info(f"调用 DeepSeek 分类，内容长度: {len(chat_content)}")

            response = self.deep_client.chat.completions.create(
                model=self.deep_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的项目分类专家，严格按 JSON 格式返回结果。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.DEEPSEEK_TEMPERATURE,
                response_format={"type": "json_object"}
            )

            result_content = response.choices[0].message.content
            logger.debug(f"DeepSeek 响应: {result_content[:200]}...")

            # 解析 JSON
            return self._parse_response(result_content)

        except Exception as e:
            logger.error(f"DeepSeek 调用失败: {e}", exc_info=True)
            return self._get_default_result()

    def _parse_response(self, content: str) -> dict:
        """解析响应"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 提取 JSON
            json_match = re.search(r"\{[\s\S]*}", content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            logger.error(f"无法解析 JSON: {content[:500]}")
            return self._get_default_result()

    @staticmethod
    def _get_default_result() -> dict:
        """默认结果"""
        return {
            "project": {"category": "未识别", "confidence": 0.0, "reason": "无法确定", "matched_rule": "",
                        "is_special": False},
            "customer": {"category": "未识别", "confidence": 0.0, "reason": "无法确定", "matched_rule": "",
                         "is_special": False},
            "need_clarification": False,
            "clarification_question": None,
            "extracted_info": {
                "search_query": None, "ip_location": None, "phone": None,
                "device_name": None, "quantity": None, "intent": None, "is_company": None
            }
        }

    def classify_with_ark(self, chat_content: str) -> Dict:
        """调用火山引擎进行分类"""
        prompt = analysis.build_classification_prompt(chat_content)
        try:
            response = self.ask_client.responses.create(
                model=settings.COZE_MODEL_ID,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                # 可选：关闭深度思考
                # thinking={"type": "disabled"},
            )

            # 提取返回内容
            output_text = ""
            if hasattr(response, "output") and response.output:
                for item in response.output:
                    if hasattr(item, "content"):
                        for content_item in item.content:
                            if hasattr(content_item, "text"):
                                output_text += content_item.text

            if not output_text and hasattr(response, "text"):
                output_text = response.text

            # 提取JSON
            json_match = re.search(r"\{.*}", output_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # 验证并修正样品分类
                sample_result = sample.parse_llm_result(result)
                result["sample"] = sample_result

                # 验证并修正材质分类
                material_result = materials.parse_llm_result(result)
                result["material"] = material_result
                return result
            else:
                return json.loads(output_text)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"大模型调用异常: {str(e)}")

# 创建全局 Coze 服务实例
coze_service = Coze()
