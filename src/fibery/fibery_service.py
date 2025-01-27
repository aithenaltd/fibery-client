import asyncio
import logging
from collections.abc import Sequence
from typing import Any, cast

import httpx

from .builders import EntityBuilder, QueryBuilder
from .config import FiberyConfig
from .entity_model import FiberyBaseModel, RichTextField
from .fibery_formats import DocumentFormat
from .fibery_models import (
    DocumentResponse,
    FiberyError,
    FiberyResponse,
    FiberyUploadError,
    QueryResponse,
    T,
)

logger = logging.getLogger(__name__)


class FiberyService:
    def __init__(self, token: str | None = None, account: str | None = None):
        self.config = FiberyConfig(token=token, account=account)
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=self.config.headers
        )

    async def __aenter__(self) -> 'FiberyService':
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.aclose()

    async def get_document_secret(
            self,
            type_name: str,
            entity_id: str,
            field_name: str
    ) -> str | None:
        try:
            query = QueryBuilder.build_document_query(type_name, entity_id, field_name)
            response = await self.client.post('/api/commands', json=[query])
            result = response.json()
            return DocumentResponse.from_raw_response(result[0], field_name)
        except httpx.HTTPError as error:
            raise FiberyError(f'Failed to get document secret: {error}') from error

    async def update_document(
            self,
            document_secret: str,
            content: str,
            document_format: DocumentFormat = DocumentFormat.MARKDOWN
    ) -> bool:
        try:
            response = await self.client.put(
                f'/api/documents/{document_secret}',
                params={'format': str(document_format)},
                json={'content': content}
            )
            result = response.json()
            return isinstance(result, dict) and 'success' in result
        except httpx.HTTPError as error:
            raise FiberyError(f'Failed to update document: {error}') from error

    async def create_entity(
            self,
            item: FiberyBaseModel,
            type_name: str
    ) -> tuple[str, FiberyResponse]:
        try:
            entity_id, command = EntityBuilder.prepare_command(type_name, item)
            response = await self.client.post('/api/commands', json=[command.model_dump()])
            result = response.json()
            result_list = cast(list, result)

            return entity_id, FiberyResponse(
                success=result_list[0].get('success'),
                result=result_list[0],
            )
        except httpx.HTTPError as error:
            raise FiberyError(f'Failed to create entity: {error}') from error

    async def _update_rich_text_fields(
            self,
            entity_id: str,
            type_name: str,
            field_contents: dict[str, RichTextField]
    ) -> None:
        for field_name, rich_text in field_contents.items():
            try:
                secret = await self.get_document_secret(
                    type_name=type_name,
                    entity_id=entity_id,
                    field_name=field_name
                )
                if secret:
                    await self.update_document(
                        document_secret=secret,
                        content=rich_text.content,
                        document_format=rich_text.format
                    )
            except Exception as e:
                logger.error(f'Error updating field {field_name}: {e}')

    async def upload_entity(
            self,
            model: FiberyBaseModel,
            type_name: str,
    ) -> str:
        try:
            entity_id, response = await self.create_entity(model, type_name)
            if not response.success:
                raise FiberyUploadError(f'Failed to create entity: {response.result}')

            await self._update_rich_text_fields(
                entity_id=entity_id,
                type_name=type_name,
                field_contents=model.get_rich_text_content()
            )
            return entity_id

        except Exception as error:
            raise FiberyUploadError(f'Failed to upload documents for {model}: {error}') from error

    async def upload_sequential(
            self,
            data_list: list[FiberyBaseModel],
            type_name: str,
            delay: float = 0.5
    ) -> None:
        for model in data_list:
            try:
                await self.upload_entity(
                    model=model,
                    type_name=type_name,
                )
            except Exception as error:
                raise FiberyUploadError(f'Failed to upload entity {model}: {error}') from error

            await asyncio.sleep(delay)

    async def query_entities(
            self,
            type_name: str,
            fields: Sequence[str | dict[Any, Any]],
            model_class: type[T],
            where: list[Any] | None = None,
            order_by: list[list[Any]] | None = None,
            limit: int | str = 'q/no-limit',
            offset: int | None = None,
            params: dict | None = None
    ) -> QueryResponse[T]:
        query = QueryBuilder.build_entities_query(
            type_name=type_name,
            fields=fields,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
            params=params
        )
        response = await self.client.post('/api/commands', json=[query])
        print(response)
        result = response.json()
        print(result)
        result_list = cast(list, result)
        return QueryResponse.from_raw_response(result_list[0], model_class)

    async def get_entities(
            self,
            type_name: str,
            fields: Sequence[str],
            model_class: type[T],
            limit: int = 100
    ) -> QueryResponse[T]:
        return await self.query_entities(
            type_name=type_name,
            fields=fields,
            model_class=model_class,
            limit=limit
        )

    async def get_filtered_entities(
            self,
            type_name: str,
            fields: Sequence[str],
            model_class: type[T],
            field_name: str,
            operator: str,
            value: Any,
            limit: int = 100
    ) -> QueryResponse[T]:
        query = QueryBuilder.build_filtered_query(
            type_name=type_name,
            fields=fields,
            field_name=field_name,
            operator=operator,
            value=value,
            limit=limit
        )
        response = await self.client.post('/api/commands', json=[query])
        print(response)
        result = response.json()
        print(result)
        result_list = cast(list, result)
        return QueryResponse.from_raw_response(result_list[0], model_class)

    async def get_entities_by_date_range(
            self,
            type_name: str,
            fields: Sequence[str],
            model_class: type[T],
            date_field: str,
            start_date: str | Any,
            end_date: str | Any,
            limit: int = 100
    ) -> QueryResponse[T]:
        query = QueryBuilder.build_date_range_query(
            type_name=type_name,
            fields=fields,
            date_field=date_field,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        response = await self.client.post('/api/commands', json=[query])
        result = response.json()
        result_list = cast(list, result)
        return QueryResponse.from_raw_response(result_list[0], model_class)
