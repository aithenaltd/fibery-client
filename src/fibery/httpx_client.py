from typing import Any

import httpx

from .client_interface import HTTPClient


class HttpxClient(HTTPClient):
    def __init__(self, headers: dict[str, str], base_url: str) -> None:
        self.client = httpx.AsyncClient(headers=headers, base_url=base_url)

    async def post(self, url: str, json: Any) -> dict[str, Any]:
        response = await self.client.post(url, json=json)
        response.raise_for_status()
        return response.json()  # type: ignore

    async def put(self, url: str, params: dict[str, Any], json: Any) -> dict[str, Any]:
        response = await self.client.put(url, params=params, json=json)
        return response.json()  # type: ignore
