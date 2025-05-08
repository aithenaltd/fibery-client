from enum import Enum


class DocumentFormat(str, Enum):
    MARKDOWN = 'md'
    HTML = 'html'
    JSON = 'json'

    def __str__(self) -> str:
        return self.value


class CollectionOperation(str, Enum):
    ADD = 'add'
    REMOVE = 'remove'

    def __str__(self) -> str:
        return self.value

    @property
    def command(self) -> str:
        command_map = {
            CollectionOperation.ADD: 'fibery.entity/add-collection-items',
            CollectionOperation.REMOVE: 'fibery.entity/remove-collection-items'
        }
        return command_map[self]
