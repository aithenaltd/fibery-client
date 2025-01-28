from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from .entity_model import FiberyBaseModel
from .fibery_models import FiberyCommand


class QueryBuilder:
    @staticmethod
    def build_document_query(type_name: str, entity_id: str, field_name: str) -> dict[str, Any]:
        return {
            'command': 'fibery.entity/query',
            'args': {
                'query': {
                    'q/from': type_name,
                    'q/select': [
                        'fibery/id',
                        {field_name: ['Collaboration~Documents/secret']}
                    ],
                    'q/where': ['=', ['fibery/id'], '$id'],
                    'q/limit': 1
                },
                'params': {'$id': entity_id}
            }
        }

    @staticmethod
    def build_entities_query(
        type_name: str,
        fields: Sequence[str | dict[str, Any]],
        where: list[Any] | dict[str, Any] | None = None,
        order_by: list[list[Any]] | None = None,
        limit: int | str = 'q/no-limit',
        offset: int | None = None,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            'q/from': type_name,
            'q/select': list(fields),  # Convert Sequence to List
            'q/limit': limit
        }

        if where is not None:
            query['q/where'] = where
        if order_by is not None:
            query['q/order-by'] = order_by
        if offset is not None:
            query['q/offset'] = offset

        command: dict[str, Any] = {
            'command': 'fibery.entity/query',
            'args': {
                'query': query
            }
        }

        if params is not None:
            command['args']['params'] = params

        return command

    @staticmethod
    def build_filtered_query(
        type_name: str,
        fields: Sequence[str],
        field_name: str,
        operator: str,
        value: Any,
        limit: int = 100
    ) -> dict[str, Any]:
        return QueryBuilder.build_entities_query(
            type_name=type_name,
            fields=fields,
            where=[operator, [field_name], '$value'],
            limit=limit,
            params={'$value': value}
        )

    @staticmethod
    def build_date_range_query(
        type_name: str,
        fields: Sequence[str],
        date_field: str,
        start_date: str | Any,
        end_date: str | Any,
        limit: int = 100
    ) -> dict[str, Any]:
        return QueryBuilder.build_entities_query(
            type_name=type_name,
            fields=fields,
            where=[
                'and',
                ['>=', [date_field], '$start_date'],
                ['<=', [date_field], '$end_date']
            ],
            limit=limit,
            params={
                '$start_date': start_date,
                '$end_date': end_date
            }
        )


class EntityBuilder:
    @staticmethod
    def prepare_command(type_name: str, data: FiberyBaseModel) -> tuple[str, FiberyCommand]:
        entity_id = str(uuid4())
        command = FiberyCommand(
            command='fibery.entity/create',
            args={
                'type': type_name,
                'entity': {
                    'fibery/id': entity_id,
                    **data.to_fibery_fields(),
                }
            }
        )
        return entity_id, command


    @staticmethod
    def prepare_update_command(type_name: str, entity_id: str, updates: dict[str, Any]) -> FiberyCommand:
        return FiberyCommand(
            command='fibery.entity/update',
            args={
                'type': type_name,
                'entity': {
                    'fibery/id': entity_id,
                    **updates
                }
            }
        )
