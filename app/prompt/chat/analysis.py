from app.prompt.chat.materials import materials
from app.prompt.chat.project import project
from app.prompt.chat.sample import sample


class Analysis:
    def __init__(self):
        self.rule = None

    @staticmethod
    def build_classification_prompt(chat_content: str) -> str:
        """构造发送给模型的Prompt"""
        # 获取项目分类与客户类型 Prompt 部分
        prompt = project.get_prompt_section()
        # 获取样品分类 Prompt 部分
        sample_prompt = sample.get_prompt_section()
        # 获取材料分类 Prompt 部分
        material_prompt = materials.get_prompt_section()

        prompt = f"""
        你是一个项目分类、客户类型识别、样品分类和材质分类专家。请根据以下规则，分析用户的聊天内容。

        {prompt['project_rules_text']}

        {prompt['customer_rules_text']}

        {sample_prompt}

        {material_prompt}

        ## 可用分类：
        - 项目分类：{prompt['project_categories']}
        - 客户类型：{prompt['customer_categories']}

        ## 判断原则：
        1. **优先级**：特殊规则 > 普通规则
        2. 如果匹配到多个规则，选择最匹配的一个
        3. 如果无法确定，返回 "未识别" 或 "待确定"
        4. 样品分类和材质分类必须从提供的列表中选择

        ## 用户聊天内容：
        {chat_content}

        ## 输出格式（严格JSON）：
        {{
            "project": {{
                "category": "识别出的项目分类",
                "confidence": 0.95,
                "reason": "判断理由",
                "matched_rule": "匹配到的具体规则描述",
                "is_special": false
            }},
            "customer": {{
                "category": "识别出的客户类型",
                "confidence": 0.90,
                "reason": "判断理由",
                "matched_rule": "匹配到的具体规则描述",
                "is_special": false
            }},
            "sample": {{
                "p_cat": "样品一级分类",
                "s_cat": "样品二级分类",
                "reason": "选择理由",
                "confidence": 0.95
            }},
            "material": {{
                "p_cat": "材质一级分类",
                "s_cat": "材质二级分类",
                "reason": "选择理由",
                "confidence": 0.95
            }},
            "need_clarification": false,
            "clarification_question": "如果需要追问，这里写问题，否则为空",
            "extracted_info": {{
                "sample": "提取的样品名称",
                "material": "提取的材质信息",
                "keywords": ["提取的关键词"],
                "has_standard": false,
                "has_instrument": false
            }}
        }}

        只返回JSON，不要有其他内容。
        """
        return prompt

analysis = Analysis()
