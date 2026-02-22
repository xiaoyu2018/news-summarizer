"""Data models for news-summarizer."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class SourceItem:
    """Unified data model for all information sources.

    Attributes:
        source_type: Type of source (e.g., "email", "reddit", "rss")
        source_id: Unique identifier for this source
        title: Title of the content
        content: Cleaned text content
        url: Original URL link (optional)
        timestamp: Publication timestamp (optional)
        raw_data: Original raw data (optional)
    """

    source_type: str
    source_id: str
    title: str
    content: str
    url: Optional[str] = None
    timestamp: Optional[datetime] = None
    raw_data: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
