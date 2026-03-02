"""Data models for news-summarizer."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SourceItem:
    """Unified data model for all information sources.

    Attributes:
        source_type: Source type (e.g., "email", "reddit", "rss")
        source_name: Human-readable source identifier (e.g., "Techmeme", "@openai", "r/technology")
        title: Content title
        content: Cleaned text content (includes URLs with context)
        published_at: Publication timestamp (optional)
        metadata: Collector-specific extended data dictionary (optional)
    """

    source_type: str
    source_name: str
    title: str
    content: str
    published_at: datetime | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_type": self.source_type,
            "source_name": self.source_name,
            "title": self.title,
            "content": self.content,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "metadata": self.metadata or {},
        }

    def to_str(self) -> str:
        """Convert to standardized string format for AI prompt generation.

        Uses model field names as keys to match references in prompt templates:
        source_type, source_name, title, content, published_at

        Returns:
            Standardized string representation
        """
        lines = [
            f"source_type: {self.source_type}",
            f"source_name: {self.source_name}",
            f"title: {self.title}",
            f"content: {self.content}",
        ]
        if self.published_at:
            lines.append(f"published_at: {self.published_at.isoformat()}")
        return "\n".join(lines)
