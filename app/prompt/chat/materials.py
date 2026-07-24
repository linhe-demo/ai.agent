from typing import Dict, Optional

from app.pkg.redis_client import redis_client, logger


class Materials:

    def __init__(self):
        self.categories = None
        self.init()

    def init(self):
        try:
            category = redis_client.get_rules("match:material")
            if category:
                self.categories = category
            else:
                logger.warning("⚠️ Redis 中无材料分类数据")
        except Exception as e:
            logger.error(f"❌ 从 Redis 加载材料分类失败: {e}")


    def get_categories_text(self) -> str:
        """获取分类文本（用于构建 Prompt）"""
        if not self.categories:
            return "暂无分类数据"

        lines = []
        for item in self.categories:
            p_cat = item.get("p_cat", "未知")
            s_cats = item.get("s_cat", [])
            lines.append(f"- {p_cat}：{', '.join(s_cats)}")

        return "\n".join(lines)

    def get_prompt_section(self) -> str:
        """获取 Prompt 中的材质分类部分"""
        return f"""
            ## 材质分类规则：
            请根据聊天内容，从以下分类中选择最匹配的材质一级分类（p_cat）和二级分类（s_cat）：
        
            {self.get_categories_text()}
        
            ### 分类原则：
            1. 如果聊天内容明确提到了材质名称，根据材质名称选择分类
            2. 如果提到产品名称，根据产品的主要材质选择分类
            3. 如果提到检测项目，根据检测对象的主要材质选择分类
            4. 如果无法确定，返回 "待确定"
            5. 一级分类和二级分类都必须从上面的列表中选择
            6. 如果都不匹配，一级分类选"其他"，二级分类选"其他"
        
            ### 输出格式：
            "material": {{
                "p_cat": "一级分类名称",
                "s_cat": "二级分类名称",
                "reason": "选择理由",
                "confidence": 0.95
            }}
            """

    def parse_llm_result(self, llm_result: Dict) -> Dict:
        """
        解析大模型返回的材质分类结果，并验证是否在分类列表中

        Returns:
            {
                "p_cat": "一级分类",
                "s_cat": "二级分类",
                "reason": "理由",
                "confidence": 0.95,
                "is_valid": True,
                "is_unknown": False
            }
        """
        material_classification = llm_result.get("material", {})

        if not material_classification:
            return {
                "p_cat": "未知",
                "s_cat": "未知",
                "reason": "大模型未返回分类结果",
                "confidence": 0.0,
                "is_valid": False,
                "is_unknown": True
            }

        p_cat = material_classification.get("p_cat", "")
        s_cat = material_classification.get("s_cat", "")
        reason = material_classification.get("reason", "")
        confidence = material_classification.get("confidence", 0.0)

        # 验证分类是否有效
        is_valid = self._validate_category(p_cat, s_cat)

        if not is_valid:
            # 尝试修正
            corrected = self._correct_category(p_cat, s_cat)
            if corrected:
                return {
                    **corrected,
                    "reason": f"原分类无效，已自动修正: {reason}",
                    "is_valid": True,
                    "is_unknown": False
                }

        return {
            "p_cat": p_cat if is_valid else "未知",
            "s_cat": s_cat if is_valid else "未知",
            "reason": reason,
            "confidence": confidence,
            "is_valid": is_valid,
            "is_unknown": not is_valid
        }

    def _validate_category(self, p_cat: str, s_cat: str) -> bool:
        """验证分类是否有效"""
        if not self.categories:
            return False

        for item in self.categories:
            if item.get("p_cat") == p_cat:
                s_cats = item.get("s_cat", [])
                if s_cat in s_cats:
                    return True
                # 如果二级分类是"其他"，也允许
                if s_cat == "其他" and "其他" in s_cats:
                    return True
        return False

    def _correct_category(self, p_cat: str, s_cat: str) -> Optional[Dict]:
        if not self.categories:
            return None
        """尝试修正分类"""
        # 如果一级分类存在，但二级分类不存在，使用"其他"
        for item in self.categories:
            if item.get("p_cat") == p_cat:
                s_cats = item.get("s_cat", [])
                if "其他" in s_cats:
                    return {
                        "p_cat": p_cat,
                        "s_cat": "其他",
                        "confidence": 0.7
                    }
                elif s_cats:
                    return {
                        "p_cat": p_cat,
                        "s_cat": s_cats[0],
                        "confidence": 0.6
                    }

        # 尝试模糊匹配一级分类
        for item in self.categories:
            if p_cat in item.get("p_cat", "") or item.get("p_cat", "") in p_cat:
                s_cats = item.get("s_cat", [])
                if "其他" in s_cats:
                    return {
                        "p_cat": item.get("p_cat"),
                        "s_cat": "其他",
                        "confidence": 0.5
                    }

        return None


materials = Materials()
