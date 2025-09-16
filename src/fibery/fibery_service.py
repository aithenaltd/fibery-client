import asyncio
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import httpx

from .builders import EntityBuilder, QueryBuilder
from .config import FiberyConfig
from .entity_model import FiberyBaseModel, RichTextField
from .fibery_models import (
    DocumentResponse,
    FiberyError,
    FiberyResponse,
    FiberyUploadError,
    FileUploadResponse,
    HttpMethod,
    QueryResponse,
    T,
    UrlUploadRequest,
)
from .utils import CollectionOperation, DocumentFormat

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FiberyService:
    def __init__(self, token: str | None = None, account: str | None = None, delay: float = 0.32):
        self.delay = delay
        self.config = FiberyConfig(token=token, account=account)
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=self.config.headers
        )

    async def __aenter__(self) -> 'FiberyService':
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.aclose()

    def get_headers(self) -> dict[str, str]:
        headers = {
            'Authorization': self.client.headers.get('authorization'),
            'X-Client': 'Unofficial JS',
            # https://gitlab.com/fibery-community/unofficial-js-client/-/blob/master/source/file.js?ref_type=heads#L21
        }
        return {k: v for k, v in headers.items() if v is not None}

    async def get_document_secret(
            self,
            type_name: str,
            entity_id: str,
            field_name: str
    ) -> str | None:
        try:
            query = QueryBuilder.build_document_query(type_name, entity_id, field_name)
            response = await self.client.post('/api/commands', json=[query])
            logger.info(response.text)
            result = response.json()
            return DocumentResponse.from_raw_response(result[0], field_name)
        except httpx.HTTPError as error:
            logger.error(error)
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
            logger.info(response.text)
            result = response.json()
            return isinstance(result, dict) and 'success' in result
        except httpx.HTTPError as error:
            logger.error(error)
            raise FiberyError(f'Failed to update document: {error}') from error

    async def create_entity(
            self,
            item: FiberyBaseModel,
            type_name: str
    ) -> tuple[str, FiberyResponse]:
        try:
            entity_id, command = EntityBuilder.prepare_command(type_name, item)
            response = await self.client.post('/api/commands', json=[command.model_dump()])
            logger.info(response.text)
            result = response.json()
            result_list = cast(list, result)

            return entity_id, FiberyResponse(
                success=result_list[0].get('success'),
                result=result_list[0],
            )
        except httpx.HTTPError as error:
            logger.error(error)
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
                    await asyncio.sleep(self.delay)
            except Exception as error:
                logger.error(f'Error updating field {field_name}: {error}')

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
            logger.error(error)
            raise FiberyUploadError(f'Failed to upload documents for {model}: {error}') from error

    async def upload_sequential(
            self,
            data_list: list[FiberyBaseModel],
            type_name: str,
    ) -> None:
        for model in data_list:
            try:
                await self.upload_entity(
                    model=model,
                    type_name=type_name,
                )
                logger.info(f'Successfully uploaded {model}')
            except Exception as error:
                logger.error(error)
                raise FiberyUploadError(f'Failed to upload entity {model}: {error}') from error

            await asyncio.sleep(self.delay)

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
        logger.info(response.text)
        result = response.json()
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
        logger.info(response.text)
        result = response.json()
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
        logger.info(response.text)
        result = response.json()
        result_list = cast(list, result)
        return QueryResponse.from_raw_response(result_list[0], model_class)

    async def update_entity(
            self,
            type_name: str,
            entity_id: str,
            updates: dict[str, Any]
    ) -> FiberyResponse:
        try:
            command = EntityBuilder.prepare_update_command(type_name, entity_id, updates)
            response = await self.client.post('/api/commands', json=[command.model_dump()])
            logger.info(response.text)
            result = response.json()
            result_list = cast(list, result)

            logger.info(f'Updating entity {entity_id}')
            return FiberyResponse(
                success=result_list[0].get('success'),
                result=result_list[0].get('result')
            )
        except httpx.HTTPError as error:
            logger.error(error)
            raise FiberyError(f'Failed to update entity: {error}') from error

    async def find_and_update_entity(
            self,
            type_name: str,
            model_class: type[T],
            search_field: str,
            search_value: Any,
            updates: dict[str, Any]
    ) -> FiberyResponse:
        try:
            response = await self.get_filtered_entities(
                type_name=type_name,
                fields=['fibery/id'],
                model_class=model_class,
                field_name=search_field,
                operator='=',
                value=search_value,
                limit=1
            )

            logger.info('Successfully found entity')
            if not response.items:
                raise FiberyError(f'Entity not found with {search_field}={search_value}')

            entity_id = response.items[0].fibery_id
            if not entity_id:
                raise FiberyError('Retrieved entity missing fibery/id')

            return await self.update_entity(
                type_name=type_name,
                entity_id=entity_id,
                updates=updates
            )
        except Exception as error:
            logger.error(error)
            raise FiberyError(f'Failed to find and update entity: {error}') from error

    async def update_collection(
            self,
            type_name: str,
            entity_id: str,
            field: str,
            item_ids: list[str],
            operation: CollectionOperation
    ) -> FiberyResponse:
        try:
            command = EntityBuilder.prepare_collection_command(
                type_name=type_name,
                entity_id=entity_id,
                field=field,
                item_ids=item_ids,
                operation=operation
            )

            response = await self.client.post(
                '/api/commands',
                json=[command.model_dump()]
            )
            logger.info(response.text)
            result = response.json()
            result_list = cast(list, result)

            return FiberyResponse(
                success=result_list[0].get('success'),
                result=result_list[0]
            )
        except httpx.HTTPError as error:
            logger.error(error)
            raise FiberyError(f'Failed to {operation} items to collection: {error}') from error

    async def add_to_collection(
            self,
            type_name: str,
            entity_id: str,
            field: str,
            item_ids: list[str]
    ) -> FiberyResponse:
        return await self.update_collection(
            type_name=type_name,
            entity_id=entity_id,
            field=field,
            item_ids=item_ids,
            operation=CollectionOperation.ADD
        )

    async def remove_from_collection(
            self,
            type_name: str,
            entity_id: str,
            field: str,
            item_ids: list[str]
    ) -> FiberyResponse:
        return await self.update_collection(
            type_name=type_name,
            entity_id=entity_id,
            field=field,
            item_ids=item_ids,
            operation=CollectionOperation.REMOVE,
        )

    async def upload_file(
            self,
            file_path: str | Path,
    ) -> FileUploadResponse:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FiberyError(f'File not found: {file_path}')

        try:
            with file_path.open('rb') as f:
                files = {'file': (file_path.name, f)}

                headers = self.get_headers()
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f'{self.client.base_url}/api/files',
                        headers=headers,
                        files=files
                    )

                logger.info(response.text)
                result = response.json()
                return FileUploadResponse.model_validate(result)

        except httpx.HTTPError as error:
            logger.error(f'HTTP error during upload: {error}')
            raise FiberyError(f'Failed to upload file: {error}') from error

        except Exception as error:
            logger.error(f'Unexpected error during upload: {error}')
            raise FiberyError(f'Failed to upload file: {error}') from error

    async def upload_from_url(
            self,
            url: str,
            name: str | None = None,
            method: HttpMethod = HttpMethod.GET,
    ) -> FileUploadResponse:
        try:
            headers = self.get_headers()
            request = UrlUploadRequest(
                url=url,
                name=name,
                method=method,
                headers=headers,
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    '/api/files/from-url',
                    json=request.model_dump(exclude_none=True)
                )
            logger.info(response.text)

            if response.status_code != 200:
                raise FiberyError(f'Upload failed with status {response.status_code}: {response.text}')

            return FileUploadResponse.model_validate(response.json())

        except Exception as error:
            logger.error(f'Failed to upload file from URL: {error}')
            raise FiberyError(f'Failed to upload file from URL: {error}') from error

    async def download_file(
            self,
            secret: str,
            destination: str | Path | None = None
    ) -> bytes:
        try:
            response = await self.client.get(f'/api/files/{secret}')
            logger.info(f'Downloaded file with secret {secret}')

            if response.status_code != 200:
                raise FiberyError(f'Download failed with status {response.status_code}: {response.text}')

            content = response.content

            if destination:
                path = Path(destination)
                path.write_bytes(content)
                logger.info(f'Saved file to {path}')

            return content

        except Exception as error:
            logger.error(f'Failed to download file: {error}')
            raise FiberyError(f'Failed to download file: {error}') from error

    async def attach_files(
            self,
            type_name: str,
            entity_id: str,
            file_ids: list[str]
    ) -> FiberyResponse:
        return await self.add_to_collection(
            type_name=type_name,
            entity_id=entity_id,
            field='Files/Files',
            item_ids=file_ids
        )
