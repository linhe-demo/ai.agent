from pydantic import BaseModel


class MatchMetadata(BaseModel):
    """项目识别元数据"""
    sample_name: str
    sample_type: str
    material_type: str
    project_name: str
    customer_name: str
    project_type: str
    customer_type: str
    company_name: str
    test_purpose: str


class MatchRequest(BaseModel):
    content: str


class MatchProject(BaseModel):
    category: str = "未识别"
    confidence: float = 0.0
    reason: str = "无法确定"
    matched_rule: str = ""
    is_special: bool = False

class MatchCustomer(BaseModel):
    category: str = "未识别"
    confidence: float = 0.0
    reason: str = "无法确定"
    matched_rule: str = ""
    is_special: bool = False

class MatchSample(BaseModel):
    p_cat: str = "未识别"
    s_cat: str = "未识别"
    reason: str = "选择理由"
    confidence: float = 0.0

class MatchMaterial(BaseModel):
    p_cat: str = "未识别"
    s_cat: str = "未识别"
    reason: str = "选择理由"
    confidence: float = 0.0


class MatchResult(BaseModel):
    project: MatchProject
    customer: MatchCustomer
    sample: MatchSample
    material: MatchMaterial
    need_clarification: bool = False
    clarification_question: str | None = None
    extracted_info: str | None = None


