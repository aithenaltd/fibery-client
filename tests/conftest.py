from typing import ClassVar
from unittest.mock import Mock

import pytest

from src import FiberyService
from src.fibery.entity_model import FiberyBaseModel
from src.fibery.utils import DocumentFormat


class FiberyModel(FiberyBaseModel):
    name: str
    description: str
    description_format: DocumentFormat = DocumentFormat.MARKDOWN

    FIBERY_FIELD_MAP: ClassVar[dict[str, str]] = {
        'name': 'TestType/name',
        'description': 'TestType/description'
    }
    RICH_TEXT_FIELDS: ClassVar[dict[str, str]] = {
        'description': 'TestType/description',
    }


class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


@pytest.fixture
def service(self, mock_client):
    service = FiberyService(token='test_token', account='test_account')
    service.client = mock_client
    return service


@pytest.fixture
def mock_client():
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_response():
    response = Mock()
    response.json.return_value = [{'success': True, 'result': {'fibery/id': 'test_id'}}]
    return response


@pytest.fixture
def test_model():
    return FiberyModel(name='Test', description='Test Description')
