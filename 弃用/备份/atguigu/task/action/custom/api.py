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
    base_url = settings.commerce_api_base_url.rstrip("/")
    url = f"{base_url}{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method, url, json=json_body)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    if isinstance(payload, dict):
        return payload
    return None
