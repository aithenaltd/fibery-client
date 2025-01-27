from typing import ClassVar
from unittest.mock import AsyncMock, Mock

import pytest

from src.fibery.entity_model import FiberyBaseModel
from src.fibery.fibery_formats import DocumentFormat


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
