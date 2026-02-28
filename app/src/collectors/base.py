"""Base collector abstract class."""

from abc import ABC, abstractmethod
from typing import Any

from app.src.models import SourceItem
from app.src.utils.logger import get_logger


class Collector(ABC):
    """Abstract base class for all collectors."""

    def __init__(self, config: dict[str, Any], name: str):
        """Initialize the collector.

        Args:
            config: Collector configuration dictionary
            name: Unique name for this collector instance
        """
        self.config = config
        self.name = name
        self.logger = get_logger(f"collector.{name}")

    @abstractmethod
    def collect(self) -> list[SourceItem]:
        """Collect items from the source.

        Returns:
            List of SourceItem objects
        """
        pass

    @property
    def source_type(self) -> str:
        """Get the source type identifier."""
        return self.config.get("type", "unknown")
