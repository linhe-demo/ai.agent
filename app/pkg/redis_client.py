import json
import logging
from typing import Optional, Dict, Any
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 客户端单例"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化 Redis 连接"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,  # 自动解码为字符串
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.client.ping()
            logger.info(f"✅ Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"❌ Redis 连接失败: {e}")
            raise

    def set_rules(self, key: str, rules: Dict[str, Any]) -> bool:
        """将规则存储到 Redis（永不过期）"""
        try:
            key = settings.REDIS_RULE_KEY + key
            value = json.dumps(rules, ensure_ascii=False, default=str)
            # 先删除旧的 key（如果有）
            self.client.delete(key)
            # 重新设置，不指定过期时间
            self.client.set(key, value)
            logger.info(f"✅ 规则已缓存到 Redis (key: {key})，永不过期")
            return True
        except Exception as e:
            logger.error(f"❌ 存储规则到 Redis 失败: {e}")
            return False

    def get_rules(self, key: str) -> Optional[Dict[str, Any]]:
        """从 Redis 获取规则"""
        try:
            key = settings.REDIS_RULE_KEY + key
            value = self.client.get(key)
            if value:
                rules = json.loads(value)
                logger.info(f"✅ 从 Redis 加载规则成功 (key: {key})")
                return rules
            else:
                logger.warning(f"⚠️ Redis 中未找到规则 (key: {key})")
                return None
        except Exception as e:
            logger.error(f"❌ 从 Redis 获取规则失败: {e}")
            return None

    def delete_rules(self, key: str) -> bool:
        """删除 Redis 中的规则"""
        try:
            key = settings.REDIS_RULE_KEY + key
            self.client.delete(key)
            logger.info(f"✅ Redis 规则已删除 (key: {key})")
            return True
        except Exception as e:
            logger.error(f"❌ 删除 Redis 规则失败: {e}")
            return False

    def is_healthy(self) -> bool:
        """检查 Redis 是否健康"""
        try:
            return self.client.ping()
        except:
            return False


# 全局 Redis 客户端实例
redis_client = RedisClient()