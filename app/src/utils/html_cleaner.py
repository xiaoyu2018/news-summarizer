"""HTML cleaning utilities."""

import html2text


class HTMLCleaner:
    """Utility class for cleaning HTML content."""

    def __init__(self):
        """Initialize HTML cleaner with default settings."""
        self._converter = html2text.HTML2Text()
        self._converter.ignore_links = False
        self._converter.ignore_images = True
        self._converter.ignore_emphasis = False
        self._converter.body_width = 0
        self._converter.unicode_snob = True

    def clean(self, html_content: str) -> str:
        """Convert HTML to clean plain text.

        Args:
            html_content: HTML content to clean

        Returns:
            Cleaned plain text
        """
        if not html_content:
            return ""

        text = self._converter.handle(html_content)
        text = self._normalize_whitespace(text)
        return text.strip()

    def clean_simple(self, text: str) -> str:
        """Clean text without HTML conversion.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        return self._normalize_whitespace(text).strip()

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized whitespace
        """
        import re

        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text


def clean_html(html_content: str) -> str:
    """Convenience function to clean HTML content.

    Args:
        html_content: HTML content to clean

    Returns:
        Cleaned plain text
    """
    cleaner = HTMLCleaner()
    return cleaner.clean(html_content)
