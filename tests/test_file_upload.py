from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src import FiberyService


class TestFiberyServiceUploadFile:
    @pytest.fixture
    def service(self, mock_client):
        service = FiberyService(token='test_token', account='test_account')
        service.client = mock_client
        return service

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_upload_file_success(self, mock_async_client_class, service, mock_client, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        mock_async_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_async_client_instance

        mock_response = Mock()
        mock_response.text = 'response text'
        mock_response.json.return_value = {
            'fibery/id': '123',
            'fibery/name': 'test.txt',
            'fibery/content-type': 'text/plain',
            'fibery/secret': 'abc123'
        }
        mock_async_client_instance.post.return_value = mock_response

        mock_client.base_url = 'https://test_account.fibery.io'
        service.get_headers = Mock(return_value={
            'Authorization': 'Bearer test',
            'X-Client': 'Unofficial JS'
        })

        result = await service.upload_file(test_file)

        mock_async_client_instance.post.assert_called_once()
        call_args = mock_async_client_instance.post.call_args

        assert call_args[1]['headers'] == {
            'Authorization': 'Bearer test',
            'X-Client': 'Unofficial JS'
        }
        assert 'file' in call_args[1]['files']
        assert call_args[1]['files']['file'][0] == 'test.txt'

        assert result.id == '123'
        assert result.name == 'test.txt'
        assert result.content_type == 'text/plain'
        assert result.secret == 'abc123'

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_upload_file_with_path_object(self, mock_async_client_class, service, mock_client, tmp_path):
        test_file = Path(tmp_path) / 'test.txt'
        test_file.write_text('test content')

        mock_async_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_async_client_instance

        mock_response = Mock()
        mock_response.json.return_value = {
            'fibery/id': '123',
            'fibery/name': 'test.txt',
            'fibery/content-type': 'text/plain',
            'fibery/secret': 'abc123'
        }
        mock_async_client_instance.post.return_value = mock_response

        mock_client.base_url = 'https://test_account.fibery.io'
        mock_client.headers = {'Authorization': 'Bearer test', 'X-Client': 'Unofficial JS'}

        await service.upload_file(test_file)

        mock_async_client_instance.post.assert_called_once()
