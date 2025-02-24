# Fibery Client

An async Python client for the Fibery API with support for entity management, document handling and complex queries.

## Features

- Asynchronous API client using `httpx`
- Type-safe entity management with Pydantic models
- Rich text document handling
- Complex query builder for filtered searches
- Date range querying support
- Sequential upload with rate limiting
- Comprehensive error handling

## Installation

```bash
pip install git+ssh://git@github.com/aithenaltd/fibery-client.git
```

## Quick Start

```python
from fibery import FiberyService
from typing import ClassVar
from fibery.entity_model import FiberyBaseModel
from fibery.utils import DocumentFormat


# Define your entity model
class EntityData(FiberyBaseModel):
    # Basic fields
    name: str
    url: str

    # Optional fields
    optional_description: str | None

    # Rich text fields (if needed)
    long_text: str
    long_text_format: DocumentFormat = DocumentFormat.MARKDOWN

    # Fibery mapping
    FIBERY_FIELD_MAP: ClassVar[dict[str, str]] = {
        'name': 'YOUR_SPACE/Name',
        'url': 'YOUR_SPACE/URL',
        'optional_description': 'YOUR_SPACE/Description',
    }

    # Rich text mapping
    RICH_TEXT_FIELDS: ClassVar[dict[str, str]] = {
        'long_text': 'YOUR_SPACE/Text',
    }


# Initialize the service
async with FiberyService(token='your_token', account='your_account') as service:
    # Create a new entity
    entity = EntityData(
        name='Test Entity',
        url='https://example.com',
        optional_description='Optional description',
        long_text='Detailed content here...'
    )

    # Upload the entity
    entity_id = await service.upload_entity(
        model=entity,
        type_name='YOUR_SPACE/Type'
    )
```

## Usage Examples

### Query Entities

Fibery operators: https://the.fibery.io/@public/User_Guide/Guide/Entity-API-264/anchor=Filter-Entities--38afb672-fb3b-4c59-800d-8c34b4e528f9

```python
async with FiberyService(token='your_token') as service:
    # Get all entities
    response = await service.get_entities(
        type_name='YOUR_SPACE/Type',
        fields=['YOUR_SPACE/Name', 'YOUR_SPACE/URL'],
        model_class=EntityData,
        limit=100
    )
    
    # Filter entities
    filtered = await service.get_filtered_entities(
        type_name='YOUR_SPACE/Type',
        fields=['YOUR_SPACE/Name'],
        model_class=EntityData,
        field_name='YOUR_SPACE/Name',
        operator='q/contains',
        value='test',
    )

    # Update entity
    await service.update_entity(
        type_name='YOUR_SPACE/Type',
        entity_id="39d2b777-0edf-4391-a0dd-ae11f82b85a0",
        updates={
            'YOUR_SPACE/Name': 'New name',
        },
    )
    
    # Find and update entity
    await service.find_and_update_entity(
        type_name='YOUR_SPACE/Type',
        model_class=EntityData,
        search_field='YOUR_SPACE/Name',
        search_value='Old name',
        updates={
            'YOUR_SPACE/Name': 'New name',
        },
    )
```

### Date Range Queries

```python
response = await service.get_entities_by_date_range(
    type_name='YOUR_SPACE/Type',
    fields=['YOUR_SPACE/Name'],
    model_class=EntityData,
    date_field='YOUR_SPACE/CreatedOn',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

### Batch Upload with Rate Limiting

```python
entities = [
    EntityData(name='Entity 1', url='https://example1.com', long_text='Content 1'),
    EntityData(name='Entity 2', url='https://example2.com', long_text='Content 2')
]

await service.upload_sequential(
    data_list=entities,
    type_name='YOUR_SPACE/Type',
    delay=0.5  # 500ms delay between uploads
)
```

### Collection operations

```python
# Add items to a collection
await service.add_to_collection(
    type_name='YOUR_SPACE/Type',
    entity_id='216c2a00-9752-11e9-81b9-4363f716f666',
    field='YOUR_SPACE/Name',
    item_ids=['0a3ae1c0-97fa-11e9-81b9-4363f716f666'],
)

# Or use the update_collection method directly
await service.update_collection(
    type_name='YOUR_SPACE/Type',
    entity_id='216c2a00-9752-11e9-81b9-4363f716f666',
    field='YOUR_SPACE/Name',
    item_ids=['0a3ae1c0-97fa-11e9-81b9-4363f716f666'],
    operation=CollectionOperation.ADD,
)
```

### Files operations

```python
# Upload a local file
await service.upload_file('path/to/file.jpg')

# Upload from URL
await service.upload_from_url(
    url='https://example.com/file.pdf',
    name='name.pdf',
)

# Download a file
await service.download_file(
    secret='c5815fb0-997e-11e9-bcec-8fb5f642f8a5',
    destination='downloaded_file.jpg',
)

# Attach files to an entity
await service.attach_files(
    type_name='YOUR_SPACE/Type',
    entity_id='20f9b920-9752-11e9-81b9-4363f716f666',
    file_ids=['c5bc1ec0-997e-11e9-bcec-8fb5f642f8a5'],
)
```

## Configuration

The client can be configured using environment variables:

```env
FIBERY_TOKEN=your_token
FIBERY_ACCOUNT=your_account
```

Or passed directly to the FiberyService constructor:

```python
service = FiberyService(
    token='your_token',
    account='your_account'
)
```

## Development

### Requirements

- Python 3.11+
- Poetry for dependency management

### Setup

1. Clone the repository
```bash
git clone https://github.com/aithenaltd/fibery-client.git
cd fibery-client
```

2. Install dependencies
```bash
poetry install
```

3. Run tests
```bash
poetry run pytest
```

## todo

- Add logger level setting
- Split FiberyService to smaller pieces
- Split test class to smaller pieces

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository.
