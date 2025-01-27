"""
Fibery API Client

An asynchronous Python client for interacting with the Fibery API. This client provides
a comprehensive interface for managing entities, documents, and executing complex queries
in Fibery.

Features:
- Async/await support using httpx
- Document management (creation, updates)
- Entity creation and querying
- Rich text field handling
- Batch upload capabilities
- Complex query builder
- Type-safe responses using Pydantic models

Basic Usage:
    ```python
    from fibery_client import FiberyService

    async with FiberyService(token="your_token", account="your_account") as service:
        # Query entities
        response = await service.get_entities(
            type_name="Type.Entity",
            fields=["field1", "field2"],
            model_class=YourModel
        )

        # Create entity
        entity_id = await service.upload_entity(
            model=your_model,
            type_name="Type.Entity"
        )

        # Update document
        await service.update_document(
            document_secret="secret",
            content="# New content",
            document_format=DocumentFormat.MARKDOWN
        )
    ```

For more information, visit: https://github.com/aithenaltd/fibery-client
"""

from fibery.entity_model import FiberyBaseModel
from fibery.fibery_formats import DocumentFormat
from fibery.fibery_models import (
    DocumentResponse,
    FiberyError,
    FiberyResponse,
    FiberyUploadError,
    QueryResponse,
)
from fibery.fibery_service import FiberyService

__version__ = "0.1.0"
__author__ = "Aithena"

__all__ = [
    "DocumentFormat",
    "DocumentResponse",
    "FiberyBaseModel",
    "FiberyError",
    "FiberyResponse",
    "FiberyService",
    "FiberyUploadError",
    "QueryResponse",
]
