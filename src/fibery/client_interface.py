from abc import ABC, abstractmethod
from typing import Any


class HTTPClient(ABC):
    @abstractmethod
    async def post(self, url: str, json: Any) -> dict[str, Any]:
        pass

    @abstractmethod
    async def put(self, url: str, params: dict[str, Any], json: Any) -> dict[str, Any]:
        pass
