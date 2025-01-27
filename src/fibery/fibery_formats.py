from enum import Enum


class DocumentFormat(str, Enum):
    MARKDOWN = 'md'
    HTML = 'html'
    JSON = 'json'

    def __str__(self) -> str:
        return self.value
