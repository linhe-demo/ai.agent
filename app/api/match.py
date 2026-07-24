import logging
import time

from fastapi import APIRouter, HTTPException

from app.services.coze_service import coze_service
from app.models.match import *
from app.models.response import ResponseModel
from app.utils.com_utils import decode_base64_content, text_to_base64
from app.utils.match_utils import match_result

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/parse/project")
async def parse_project(request: MatchRequest) -> ResponseModel:
    if not request.content or len(request.content.strip()) < 2:
        return ResponseModel(
            code=400,
            message="聊天内容不能为空",
            data=[]
        )

    default_result2 = MatchResult(
        project=MatchProject(),
        customer=MatchCustomer(),
        sample=MatchSample(),
        material=MatchMaterial(),
        need_clarification=False,
        clarification_question=None,
        extracted_info=None
    )

    message = decode_base64_content(request.content)
    try:
        # start_time = time.time()
        # result1 = coze_service.classify_with_deepseek(message)
        # end_time = time.time()
        # elapsed = end_time - start_time
        # logger.info(f"✅ DeepSeek 耗时: {elapsed:.3f} 秒")  # 用 logger.info


        start_time2 = time.time()
        result2 = coze_service.classify_with_ark(message)
        end_time2 = time.time()
        elapsed2 = end_time2 - start_time2
        logger.info(f"✅ 火山引擎 耗时: {elapsed2:.3f} 秒")  # 用 logger.info

    except Exception as e:
        logger.error(f"Coze 服务调用失败: {e}", exc_info=True)
        return ResponseModel(
            code=400,
            message=str(e),
            data=[]
        )

    if result2:
        match_result(result2, default_result2)

    return ResponseModel(
        code=200,
        data=default_result2
    )
