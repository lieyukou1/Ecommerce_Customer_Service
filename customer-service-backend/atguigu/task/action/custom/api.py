from __future__ import annotations

from typing import Any

import httpx

from atguigu.config.config import settings


async def request_property_api(
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """
    功能：调用物业中台接口，并把响应规整成字典数据。

    输入：
    - method: HTTP 方法。
    - path: 相对接口路径。
    - json_body: 可选 JSON 请求体。

    输出：
    - dict[str, Any] | None: 成功时返回 `data` 字段或原始字典；失败时返回 None。

    调用情况：
    - 多个自定义 action 的中台查询/提交逻辑复用。

    副作用：
    - 会发起外部 HTTP 请求。
    """
    base_url = settings.commerce_api_base_url.rstrip("/")
    url = f"{base_url}{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method, url, json=json_body)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    # 优先解包后端统一响应中的 data，方便 action 层直接消费。
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    if isinstance(payload, dict):
        return payload
    return None
