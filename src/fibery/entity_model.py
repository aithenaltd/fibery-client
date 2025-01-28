from typing import Any, ClassVar

from pydantic import BaseModel

from .fibery_formats import DocumentFormat


class RichTextField(BaseModel):
    content: str
    format: DocumentFormat = DocumentFormat.MARKDOWN


class FiberyBaseModel(BaseModel):
    fibery_id: str | None = None

    FIBERY_FIELD_MAP: ClassVar[dict[str, str]] = {}
    RICH_TEXT_FIELDS: ClassVar[dict[str, str]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.FIBERY_FIELD_MAP = {
            'fibery_id': 'fibery/id',
            **cls.FIBERY_FIELD_MAP
        }

    def to_fibery_fields(self) -> dict[str, Any]:
        return {
            fibery_field: getattr(self, field_name)
            for field_name, fibery_field in self.FIBERY_FIELD_MAP.items()
            if getattr(self, field_name) is not None
        }

    def get_rich_text_content(self) -> dict[str, RichTextField]:
        result = {}
        for field_name, fibery_field in self.RICH_TEXT_FIELDS.items():
            content = getattr(self, field_name, None)
            if content is not None:
                result[fibery_field] = RichTextField(
                    content=content,
                    format=getattr(self, f'{field_name}_format', DocumentFormat.MARKDOWN)
                )
        return result
