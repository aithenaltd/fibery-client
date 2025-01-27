from unittest.mock import Mock

import pytest

from src.fibery.fibery_formats import DocumentFormat
from src.fibery.fibery_models import FiberyUploadError, QueryResponse
from src.fibery.fibery_service import FiberyService
from tests.conftest import FiberyModel


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
