"""Base sender abstract class."""

from abc import ABC, abstractmethod
from typing import Any

from src.utils.logger import get_logger


class Sender(ABC):
    """Abstract base class for all senders."""

    def __init__(self, config: dict[str, Any], name: str):
        """Initialize the sender.

        Args:
            config: Sender configuration dictionary
            name: Unique name for this sender instance
        """
        self.config = config
        self.name = name
        self.logger = get_logger(f"sender.{name}")

    @abstractmethod
    def send(self, content: str, subject: str) -> bool:
        """Send content with given subject.

        Args:
            content: Content to send
            subject: Subject line

        Returns:
            True if send was successful
        """
        pass

    @property
    def enabled(self) -> bool:
        """Check if this sender is enabled."""
        return self.config.get("enabled", True)
