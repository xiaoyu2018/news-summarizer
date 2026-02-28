"""Base processor abstract class."""

from abc import ABC, abstractmethod
from typing import Any

from app.src.models import SourceItem
from app.src.utils.logger import get_logger


class Processor(ABC):
    """Abstract base class for all processors."""

    def __init__(self, config: dict[str, Any], name: str):
        """Initialize the processor.

        Args:
            config: Processor configuration dictionary
            name: Unique name for this processor instance
        """
        self.config = config
        self.name = name
        self.logger = get_logger(f"processor.{name}")

    @abstractmethod
    def process(self, items: list[SourceItem]) -> str:
        """Process source items and generate summary.

        Args:
            items: List of SourceItem objects

        Returns:
            Processed summary text
        """
        pass
