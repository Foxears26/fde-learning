"""带超时和 HTTP 状态码重试的同步客户端。"""

import logging
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx


logger = logging.getLogger(__name__)


class APIClient:
    """GET 返回 httpx.Response；失败时保留 httpx 的原始异常。

    max_retries 是首次请求之后的重试次数，默认最多请求 4 次。
    timeout 可传秒数或 httpx.Timeout；默认 connect=5、read/write/pool=10。
    transport 用于注入 MockTransport，with 语句会自动释放连接。
    """

    def __init__(
        self,
        base_url: str,
        timeout: float | httpx.Timeout | None = None,
        max_retries: int = 3,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if isinstance(max_retries, bool) or not isinstance(max_retries, int):
            raise TypeError("max_retries 必须是整数")
        if max_retries < 0:
            raise ValueError("max_retries 不能小于 0")
        self.max_retries = max_retries
        self._client = httpx.Client(
            base_url=base_url,
            timeout=httpx.Timeout(10.0, connect=5.0) if timeout is None else timeout,
            transport=transport,
        )

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        """无效 Retry-After 回退到指数退避；过去的日期无需等待。"""
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        value = value.strip()
        if value.isascii() and value.isdigit():
            return float(value)
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None

    def get(self, path: str) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            # 不捕获网络/超时异常：仅 HTTP 429 和 5xx 可以重试。
            response = self._client.get(path)
            retryable = response.status_code == 429 or 500 <= response.status_code < 600
            if not retryable or attempt == self.max_retries:
                response.raise_for_status()
                return response

            delay = self._retry_after(response) if response.status_code == 429 else None
            if delay is None:
                delay = 2 ** attempt + random.uniform(0.0, 0.5)
            # 有效 Retry-After 优先，直接使用服务端要求的等待时间。
            response.close()
            logger.info(
                "GET %s: HTTP %s; retry %s/%s in %.3fs (Retry-After=%r)",
                response.request.url, response.status_code, attempt + 1,
                self.max_retries, delay, response.headers.get("Retry-After"),
            )
            time.sleep(delay)

        raise AssertionError("unreachable")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
