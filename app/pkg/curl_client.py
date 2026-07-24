import json
import logging
import time
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class CurlClient(object):
    """HTTP 请求客户端（类似 curl）"""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.session = requests.Session()
        self.timeout = timeout

        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(
            self,
            method: str,
            url: str,
            params: Optional[Dict] = None,
            data: Optional[Dict] = None,
            json_data: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            timeout: Optional[int] = None,
            **kwargs
    ) -> requests.Response:
        """
        发送 HTTP 请求

        Args:
            method: 请求方法 (GET, POST, PUT, DELETE, PATCH)
            url: 请求 URL
            params: URL 查询参数
            data: form 数据
            json_data: JSON 数据
            headers: 请求头
            timeout: 超时时间
            **kwargs: 其他 requests 参数

        Returns:
            Response 对象
        """
        method = method.upper()
        headers = headers or {}

        # 默认添加 Content-Type
        if json_data and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        timeout = timeout or self.timeout

        # 记录请求日志
        logger.info(f"📤 {method} {url}")
        if params:
            logger.debug(f"  参数: {params}")
        if json_data:
            logger.debug(f"  JSON: {json_data}")
        elif data:
            logger.debug(f"  数据: {data}")

        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=timeout,
                **kwargs
            )

            elapsed = time.time() - start_time
            logger.info(f"📥 响应: {response.status_code} (耗时: {elapsed:.3f}s)")

            return response

        except requests.exceptions.Timeout:
            logger.error(f"❌ 请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ 连接失败: {url}")
            raise
        except Exception as e:
            logger.error(f"❌ 请求异常: {e}")
            raise

    def get(
            self,
            url: str,
            params: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """GET 请求"""
        return self.request("GET", url, params=params, headers=headers, **kwargs)

    def post(
            self,
            url: str,
            data: Optional[Dict] = None,
            json_data: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """POST 请求"""
        return self.request("POST", url, data=data, json_data=json_data, headers=headers, **kwargs)

    def put(
            self,
            url: str,
            data: Optional[Dict] = None,
            json_data: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """PUT 请求"""
        return self.request("PUT", url, data=data, json_data=json_data, headers=headers, **kwargs)

    def delete(
            self,
            url: str,
            params: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """DELETE 请求"""
        return self.request("DELETE", url, params=params, headers=headers, **kwargs)

    def patch(
            self,
            url: str,
            data: Optional[Dict] = None,
            json_data: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """PATCH 请求"""
        return self.request("PATCH", url, data=data, json_data=json_data, headers=headers, **kwargs)

    def post_form(
            self,
            url: str,
            data: Dict,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """POST form 表单请求"""
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        return self.post(url, data=data, headers=headers, **kwargs)

    def upload_file(
            self,
            url: str,
            file_path: str,
            field_name: str = "file",
            data: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            **kwargs
    ) -> requests.Response:
        """上传文件"""
        files = {field_name: open(file_path, "rb")}
        return self.post(url, data=data, files=files, headers=headers, **kwargs)


# 全局 HTTP 客户端实例
curl_client = CurlClient()