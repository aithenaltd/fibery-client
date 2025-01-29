from unittest.mock import Mock, patch

import httpx
import pytest

from src.fibery.fibery_models import (
    FiberyError,
    FiberyUploadError,
    FileUploadResponse,
    QueryResponse,
)
from src.fibery.fibery_service import FiberyService
from src.fibery.utils import CollectionOperation, DocumentFormat
from tests.conftest import AsyncMock, FiberyModel, MockProcess


class TestFiberyService:
    @pytest.fixture
    def service(self, mock_client):
        service = FiberyService(token='test_token', account='test_account')
        service.client = mock_client
        return service

    @pytest.mark.asyncio
    async def test_get_document_secret(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{'success': True, 'result': [{'description': {'secret': 'test_secret'}}]}]
        mock_client.post.return_value = mock_response

        result = await service.get_document_secret('TestType', 'test_id', 'description')

        assert result == 'test_secret'
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_document(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_client.put.return_value = mock_response

        result = await service.update_document(
            'test_secret',
            'test_content',
            DocumentFormat.MARKDOWN
        )

        assert result is True
        mock_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_entity(self, service, mock_client, test_model, mock_response):
        mock_client.post.return_value = mock_response

        entity_id, response = await service.create_entity(test_model, 'TestType')

        assert entity_id is not None
        assert response.success is True
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_entity_success(self, service, mock_client, test_model):
        first_response = Mock()
        first_response.json.return_value = [
            {
                'success': True,
                'result': {'fibery/id': '9ebe6ac9-79d3-46dc-b81e-0cca2e6dce32'}
            }
        ]

        second_response = Mock()
        second_response.json.return_value = [
            {
                'success': True,
                'result': [
                    {'TestType/description': {'secret': 'test_secret'}}
                ]
            }
        ]

        third_response = Mock()
        third_response.json.return_value = {'success': True}

        mock_client.post.side_effect = [first_response, second_response]
        mock_client.put.return_value = third_response

        await service.upload_entity(test_model, 'TestType')

        assert mock_client.post.call_count == 2
        assert mock_client.put.call_count == 1

    @pytest.mark.asyncio
    async def test_upload_entity_failure(self, service, mock_client, test_model):
        mock_response = Mock()
        mock_response.json.return_value = [{'success': False, 'result': 'error'}]
        mock_client.post.return_value = mock_response

        with pytest.raises(FiberyUploadError):
            await service.upload_entity(test_model, 'TestType')

    @pytest.mark.asyncio
    async def test_query_entities(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': [
                {
                    'TestType/name': 'Test',
                    'TestType/description': 'Test Description'
                }
            ]
        }]
        mock_client.post.return_value = mock_response

        response = await service.query_entities(
            type_name='TestType',
            fields=['name', 'description'],
            model_class=FiberyModel
        )

        assert isinstance(response, QueryResponse)
        assert len(response.items) > 0
        assert isinstance(response.items[0], FiberyModel)

    @pytest.mark.asyncio
    async def test_get_filtered_entities(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': [
                {
                    'TestType/name': 'Test',
                    'TestType/description': 'Test Description'
                }
            ]
        }]
        mock_client.post.return_value = mock_response

        response = await service.get_filtered_entities(
            type_name='TestType',
            fields=['name', 'description'],
            model_class=FiberyModel,
            field_name='name',
            operator='=',
            value='Test'
        )

        assert isinstance(response, QueryResponse)
        assert len(response.items) > 0
        assert isinstance(response.items[0], FiberyModel)

    @pytest.mark.asyncio
    async def test_get_entities_by_date_range(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': [
                {
                    'TestType/name': 'Test',
                    'TestType/description': 'Test Description'
                }
            ]
        }]
        mock_client.post.return_value = mock_response

        response = await service.get_entities_by_date_range(
            type_name='TestType',
            fields=['name', 'description'],
            model_class=FiberyModel,
            date_field='created_at',
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        assert isinstance(response, QueryResponse)
        assert len(response.items) > 0
        assert isinstance(response.items[0], FiberyModel)

    @pytest.mark.asyncio
    async def test_update_entity(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': {
                'fibery/id': 'test_id',
                'TestType/name': 'Updated Name'
            }
        }]
        mock_client.post.return_value = mock_response

        response = await service.update_entity(
            type_name='TestType',
            entity_id='test_id',
            updates={'TestType/name': 'Updated Name'}
        )

        assert response.success is True
        assert response.result['TestType/name'] == 'Updated Name'
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_and_update_entity(self, service, mock_client):
        search_response = Mock()
        search_response.json.return_value = [{
            'success': True,
            'result': [{
                'fibery/id': 'found_id',
                'TestType/name': 'Original Name',
                'TestType/description': 'Original Description'
            }]
        }]

        update_response = Mock()
        update_response.json.return_value = [{
            'success': True,
            'result': {
                'fibery/id': 'found_id',
                'TestType/name': 'Updated Name',
                'TestType/description': 'Original Description'
            }
        }]

        mock_client.post.side_effect = [search_response, update_response]

        response = await service.find_and_update_entity(
            type_name='TestType',
            model_class=FiberyModel,
            search_field='name',
            search_value='Original Name',
            updates={'TestType/name': 'Updated Name'}
        )

        assert response.success is True
        assert response.result['TestType/name'] == 'Updated Name'
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_find_and_update_entity_not_found(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': [],
        }]
        mock_client.post.return_value = mock_response

        with pytest.raises(FiberyError, match='Entity not found'):
            await service.find_and_update_entity(
                type_name='TestType',
                model_class=FiberyModel,
                search_field='name',
                search_value='Nonexistent',
                updates={'TestType/name': 'Updated Name'}
            )

    @pytest.mark.asyncio
    async def test_upload_file_success(self, service, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        mock_process = MockProcess(
            stdout=b'''
            {
                "fibery/id": "test-id-123",
                "fibery/name": "test.txt",
                "fibery/content-type": "text/plain",
                "fibery/secret": "test-secret-456"
            }
            ''',
            stderr=b'',
            returncode=0
        )

        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=mock_process)):
            response = await service.upload_file(test_file)

            assert isinstance(response, FileUploadResponse)
            assert response.id == "test-id-123"
            assert response.name == "test.txt"
            assert response.content_type == "text/plain"
            assert response.secret == "test-secret-456"

    @pytest.mark.asyncio
    async def test_upload_file_curl_error(self, service, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        mock_process = MockProcess(
            stdout=b'',
            stderr=b'curl: (22) Some curl error',
            returncode=22
        )

        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=mock_process)):
            with pytest.raises(FiberyError) as exc_info:
                await service.upload_file(test_file)
            assert 'curl error' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_invalid_json_response(self, service, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        mock_process = MockProcess(
            stdout=b'Invalid JSON response',
            stderr=b'',
            returncode=0
        )

        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=mock_process)):
            with pytest.raises(FiberyError) as exc_info:
                await service.upload_file(test_file)
            assert 'Failed to parse response JSON' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_with_spaces(self, service, tmp_path):
        test_file = tmp_path / 'test file with spaces.txt'
        test_file.write_text('test content')

        mock_process = MockProcess(
            stdout=b'''
            {
                "fibery/id": "test-id-123",
                "fibery/name": "test file with spaces.txt",
                "fibery/content-type": "text/plain",
                "fibery/secret": "test-secret-456"
            }
            ''',
            stderr=b'',
            returncode=0
        )

        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=mock_process)):
            response = await service.upload_file(test_file)
            assert response.name == 'test file with spaces.txt'

    @pytest.mark.asyncio
    async def test_upload_file_binary(self, service, tmp_path):
        test_file = tmp_path / 'test.bin'
        test_file.write_bytes(b'\x00\x01\x02\x03')

        mock_process = MockProcess(
            stdout=b'''
            {
                "fibery/id": "test-id-123",
                "fibery/name": "test.bin",
                "fibery/content-type": "application/octet-stream",
                "fibery/secret": "test-secret-456"
            }
            ''',
            stderr=b'',
            returncode=0
        )

        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=mock_process)):
            response = await service.upload_file(test_file)
            assert response.content_type == 'application/octet-stream'


    @pytest.mark.asyncio
    async def test_add_to_collection(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': 'ok'
        }]
        mock_client.post.return_value = mock_response

        response = await service.add_to_collection(
            type_name='TestType',
            entity_id='test_entity_id',
            field='user/Collection',
            item_ids=['item1', 'item2']
        )

        assert response.result == {'result': 'ok', 'success': True}
        mock_client.post.assert_called_once()

        call_args = mock_client.post.call_args
        assert call_args[0][0] == '/api/commands'
        command = call_args[1]['json'][0]
        assert command['command'] == 'fibery.entity/add-collection-items'
        assert command['args']['type'] == 'TestType'
        assert command['args']['entity']['fibery/id'] == 'test_entity_id'
        assert command['args']['field'] == 'user/Collection'
        assert len(command['args']['items']) == 2


    @pytest.mark.asyncio
    async def test_remove_from_collection(self, service, mock_client):
        mock_response = Mock()
        mock_response.json.return_value = [{
            'success': True,
            'result': 'ok'
        }]
        mock_client.post.return_value = mock_response

        response = await service.remove_from_collection(
            type_name='TestType',
            entity_id='test_entity_id',
            field='user/Collection',
            item_ids=['item1', 'item2']
        )

        assert response.result == {'result': 'ok', 'success': True}
        mock_client.post.assert_called_once()

        call_args = mock_client.post.call_args
        assert call_args[0][0] == '/api/commands'
        command = call_args[1]['json'][0]
        assert command['command'] == 'fibery.entity/remove-collection-items'
        assert command['args']['type'] == 'TestType'
        assert command['args']['entity']['fibery/id'] == 'test_entity_id'
        assert command['args']['field'] == 'user/Collection'
        assert len(command['args']['items']) == 2

    @pytest.mark.asyncio
    async def test_update_collection_error_handling(self, service, mock_client):
        mock_client.post.side_effect = httpx.HTTPError('Connection error')

        with pytest.raises(FiberyError, match='Failed to add items to collection'):
            await service.update_collection(
                type_name='TestType',
                entity_id='test_entity_id',
                field='user/Collection',
                item_ids=['item1'],
                operation=CollectionOperation.ADD
            )
