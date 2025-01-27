from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .entity_model import FiberyBaseModel

T = TypeVar('T', bound=FiberyBaseModel)

class FiberyError(Exception):
    pass


class FiberyUploadError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class FiberyCommand(BaseModel):
    command: str = 'fibery.entity/create'
    args: dict[str, Any]


class FiberyResponse(BaseModel):
    success: bool
    result: dict[str, Any]


class QueryResult(BaseModel):
    success: bool
    result: list[dict[str, Any]] | None = None
    error: dict[str, Any] | None = None


class QueryResponse(Generic[T]):
    def __init__(
            self,
            data: list[dict[str, Any]],
            model_class: type[T],
    ) -> None:
        transformed_data = [
            self._transform_fibery_fields(item, model_class)
            for item in data
        ]

        self.items: list[T] = [
            model_class.model_validate(item)
            for item in transformed_data
        ]
        self.total: int = len(self.items)

    @staticmethod
    def _transform_fibery_fields(data: dict[str, Any], model_class: type[T]) -> dict[str, Any]:
        reverse_map = {
            fibery_field: field_name
            for field_name, fibery_field in model_class.FIBERY_FIELD_MAP.items()
        }

        transformed = {}
        for fibery_field, value in data.items():
            if fibery_field in reverse_map:
                model_field = reverse_map[fibery_field]
                transformed[model_field] = value

        return transformed

    @classmethod
    def from_raw_response(
            cls,
            response: dict[str, Any],
            model_class: type[T],
    ) -> 'QueryResponse[T]':
        if not response.get('success'):
            raise FiberyError(f"Query failed: {response.get('error')}")

        result = response.get('result', [])
        return cls(data=result, model_class=model_class)


class DocumentSecret(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    secret: str = Field(alias='Collaboration~Documents/secret')


class DocumentResponse(BaseModel):
    field_content: DocumentSecret | None = None

    @classmethod
    def from_raw_response(
            cls,
            response: dict[str, Any],
            field_name: str
    ) -> str | None:
        if not response.get('success') or not response.get('result'):
            return None

        field_data = response['result'][0].get(field_name)
        if not field_data:
            return None

        doc = cls(field_content=DocumentSecret.model_validate(field_data))
        return doc.field_content.secret if doc.field_content else None
