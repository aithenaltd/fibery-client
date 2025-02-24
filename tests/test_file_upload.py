from pathlib import Path
from unittest.mock import Mock, PropertyMock

import pytest

from src import FiberyService


class TestFiberyServiceUploadFile:
    @pytest.fixture
    def service(self, mock_client):
        service = FiberyService(token='test_token', account='test_account')
        service.client = mock_client
        return service

    @pytest.mark.asyncio
    async def test_upload_file_success(self, service, mock_client, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        type(mock_client).headers = PropertyMock(return_value={'Authorization': 'Bearer test'})
        mock_response = Mock()
        mock_response.text = 'response text'
        mock_response.json.return_value = {
            'fibery/id': '123',
            'fibery/name': 'test.txt',
            'fibery/content-type': 'text/plain',
            'fibery/secret': 'abc123'
        }
        mock_client.post.return_value = mock_response

        result = await service.upload_file(test_file)

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == '/api/files'
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
    async def test_upload_file_with_path_object(self, service, mock_client, tmp_path):
        test_file = Path(tmp_path) / 'test.txt'
        test_file.write_text('test content')

        type(mock_client).headers = PropertyMock(return_value={'Authorization': 'Bearer test'})
        mock_response = Mock()
        mock_response.json.return_value = {
            'fibery/id': '123',
            'fibery/name': 'test.txt',
            'fibery/content-type': 'text/plain',
            'fibery/secret': 'abc123'
        }
        mock_client.post.return_value = mock_response

        await service.upload_file(test_file)

        mock_client.post.assert_called_once()
