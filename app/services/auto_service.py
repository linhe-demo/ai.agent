from pathlib import Path
from typing import Dict, List

import pandas as pd

from app.core import settings
from app.core.logging import setup_logging, get_logger
from app.pkg.curl_client import curl_client
from app.pkg.redis_client import redis_client

setup_logging()
logger = get_logger(__name__)


class AutoService:
    def __init__(self):
        self.url = settings.CRM_ZY_URL
        self.authorization = settings.CRM_ZY_AUTHORIZATION
        self.config_path = self.init_config()

    def init(self):
        # 项目分类与客户类型配置
        self.auto_load_project_and_customer_rule()
        # 样品分类配置
        self.auto_load_sample_rule()
        # 材料分类配置
        self.auto_load_materials_rule()

    @staticmethod
    def init_config():
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        config_path = BASE_DIR / "statics" / "project_match_config.xlsx"
        return str(config_path)

    def _load_rules_from_excel(self, file_path: str) -> Dict:
        """从Excel加载规则"""
        df_project = pd.read_excel(file_path, sheet_name="项目规则")
        df_customer = pd.read_excel(file_path, sheet_name="背景规则")

        result = {
            "project": {
                "normal_rules": [],
                "special_rules": [],
                "all_categories": list()
            },
            "customer": {
                "normal_rules": [],
                "special_rules": [],
                "all_categories": list()
            }
        }

        # 处理项目规则
        for _, row in df_project.iterrows():
            project = str(row["项目"]).strip()
            description = str(row["判断说明"]).strip()
            if self._is_invalid_value(project) or self._is_invalid_value(description):
                continue
            rule = {"category": project, "description": description}

            if project == "注意":
                result["project"]["special_rules"].append(rule)
            else:
                result["project"]["normal_rules"].append(rule)
                result["project"]["all_categories"].append(project)

        # 处理客户类型
        for _, row in df_customer.iterrows():
            customer_type = str(row["项目"]).strip()
            description = str(row["判断说明"]).strip()
            if self._is_invalid_value(customer_type) or self._is_invalid_value(description):
                continue

            rule = {"category": customer_type, "description": description}

            if customer_type == "注意":
                result["customer"]["special_rules"].append(rule)
            else:
                result["customer"]["normal_rules"].append(rule)
                result["customer"]["all_categories"].append(customer_type)

        # 将 set 转换为 list 以便 JSON 序列化
        result["project"]["all_categories"] = list(result["project"]["all_categories"])
        result["customer"]["all_categories"] = list(result["customer"]["all_categories"])

        return result

    @staticmethod
    def _is_invalid_value(value) -> bool:
        """
        检查值是否无效（NaN、None、空字符串、字符串"nan"等）
        """
        if value is None:
            return True
        if pd.isna(value):
            return True
        if isinstance(value, str):
            # 检查是否是 "nan"（不区分大小写）或空字符串
            if value.strip().lower() == "nan" or not value.strip():
                return True
        return False

    @staticmethod
    def _deal_crm_res(res: Dict) -> List[Dict]:
        back = []
        if res.get("status", 1) == 0:
            if len(res.get("result", [])) > 0:
                for i in res.get("result", []):
                    tmp_list = {"p_cat": i.get("Name", ""), "s_cat": []}
                    for m in i.get("ChildrenList", []):
                        tmp_list.get("s_cat", []).append(m.get("Name", ""))
                    back.append(tmp_list)
        else:
            logger.error(f"crm 接口返回异常: {res}")

        return back

    def auto_load_project_and_customer_rule(self):
        # 检查redis中是是否存在规则
        try:
            rules = redis_client.get_rules("match:project")
            if rules:
                logger.info("项目分类与客户类型配置已从redis加载......")
            else:
                rules = self._load_rules_from_excel(self.config_path)
                redis_client.set_rules("match:project", rules)
                logger.info("项目分类与客户类型配置已从excel加载......")
        except Exception as e:
            logger.error(f"项目分类与客户类型配置加载失败：{e}")

    def auto_load_sample_rule(self):
        try:
            rules = redis_client.get_rules("match:sample")
            if rules:
                logger.info("样品分类配置已从redis加载......")
            else:
                # 获取样品分类配置
                response = curl_client.get(
                    url=self.url + "/Dictionary/GetDicsWithChildList",
                    params={"pId": 9002, "cId": 9028},
                    headers={"Authorization": f"Bearer {self.authorization}"}
                )

                sample_rule = self._deal_crm_res(response.json())
                redis_client.set_rules("match:sample", sample_rule)
                logger.info("样品分类配置已从接口加载......")
        except Exception as e:
            logger.error(f"请求异常：{e}")

    def auto_load_materials_rule(self):
        try:
            rules = redis_client.get_rules("match:material")
            if rules:
                logger.info("材料分类配置已从redis加载......")
            else:
                # 获取材料分类配置
                response = curl_client.get(
                    url=self.url + "/Dictionary/GetDicsWithChildList",
                    params={"pId": 9029, "cId": 9030},
                    headers={"Authorization": f"Bearer {self.authorization}"}
                )

                sample_rule = self._deal_crm_res(response.json())
                redis_client.set_rules("match:material", sample_rule)
                logger.info("材料分类配置已从接口加载......")
        except Exception as e:
            logger.error(f"请求异常：{e}")

auto_service = AutoService()
