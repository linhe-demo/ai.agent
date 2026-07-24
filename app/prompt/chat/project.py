from typing import Dict

from app.core.logging import setup_logging, get_logger
from app.pkg.redis_client import redis_client


setup_logging()
logger = get_logger(__name__)


class Project:
    def __init__(self):
        self.rules = None
        self.init()

    def init(self):
        try:
            rules = redis_client.get_rules("match:project")
            if rules:
                self.rules = rules
            else:
                logger.warning("Redis 中无项目分类与客户类型配置数据")
        except Exception as e:
            logger.error(f"从 Redis 加载项目分类与客户类型配置数据失败: {e}")

    def get_prompt_section(self) -> Dict:
        # 格式化项目规则
        project_rules_text = "【项目分类规则】\n"
        for rule in self.rules["project"]["normal_rules"]:
            project_rules_text += f"- 如果聊天内容匹配以下描述，则分类为「{rule['category']}」：{rule['description']}\n"

        if self.rules["project"]["special_rules"]:
            project_rules_text += "\n【⚠️ 特殊规则（优先级最高）】\n"
            for rule in self.rules["project"]["special_rules"]:
                project_rules_text += f"- {rule['description']}\n"

        # 格式化客户类型规则
        customer_rules_text = "【客户类型规则】\n"
        for rule in self.rules["customer"]["normal_rules"]:
            customer_rules_text += f"- 如果聊天内容匹配以下描述，则分类为「{rule['category']}」：{rule['description']}\n"

        if self.rules["customer"]["special_rules"]:
            customer_rules_text += "\n【⚠️ 特殊规则（优先级最高）】\n"
            for rule in self.rules["customer"]["special_rules"]:
                customer_rules_text += f"- {rule['description']}\n"

        project_categories = ", ".join(self.rules["project"]["all_categories"])
        customer_categories = ", ".join(self.rules["customer"]["all_categories"])
        return {
            "project_rules_text": project_rules_text,
            "customer_rules_text": customer_rules_text,
            "project_categories": project_categories,
            "customer_categories": customer_categories,
        }

project = Project()