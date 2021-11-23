"""Dependency to extract value from message data."""
from typing import Any

from botx import Message


class _ButtonDataExtractor:
    """example: foo: int = Depends(DataExtractor('foo', 'bar')."""

    def __call__(self, item_name_to_extract: str, default: Any = None) -> Any:
        """Create function that will extract value from message button."""

        def factory(message: Message) -> Any:
            return message.data.get(item_name_to_extract, default)

        return factory


DataExtractor = _ButtonDataExtractor()
