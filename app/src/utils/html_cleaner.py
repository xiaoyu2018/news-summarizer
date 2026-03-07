"""HTML cleaning utilities."""

import html2text
import quopri
import re


class HTMLCleaner:
    """Utility class for cleaning HTML content."""

    # Newsletter navigation/footer patterns to filter
    NEWSLETTER_FILTER_PATTERNS = [
        r"unsubscribe",
        r"update.*preferences",
        r"manage.*preferences",
        r"view.*online",
        r"view.*browser",
        r"read.*online",
        r"follow.*on",
        r"facebook$",
        r"twitter$",
        r"linkedin$",
        r"instagram$",
        r"youtube$",
        r"social media",
        r"\d{4}.*LLC",
        r"all rights reserved",
        r"copyright",
        r"©",
    ]

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
        text = self._remove_newsletter_artifacts(text)
        text = self._normalize_whitespace(text)
        return text.strip()

    def clean_simple(self, text: str) -> str:
        """Clean text with quoted-printable decoding support.

        This method handles plain text emails that may use quoted-printable
        encoding (common in newsletters like Techmeme).

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Decode quoted-printable if detected
        text = self._decode_quoted_printable(text)
        text = self._normalize_whitespace(text)
        return text.strip()

    def _remove_newsletter_artifacts(self, text: str) -> str:
        """Remove table artifacts and navigation links from newsletter content.

        Args:
            text: Text with potential artifacts

        Returns:
            Text with artifacts removed
        """
        # Remove table artifacts (html2text converts empty cells to | |)
        text = re.sub(r"\|\s*\|\s*\|", "", text)
        text = re.sub(r"\|\s*\|", "", text)

        # Remove empty brackets
        text = re.sub(r"\[\s*\]", "", text)

        # Remove horizontal lines
        text = re.sub(r"^\s*[-=]{3,}\s*$", "", text, flags=re.MULTILINE)

        # Remove navigation/footer patterns (case-insensitive, whole line)
        for pattern in self.NEWSLETTER_FILTER_PATTERNS:
            # Match whole lines containing the pattern
            text = re.sub(
                rf"^.*{pattern}.*$", "", text, flags=re.IGNORECASE | re.MULTILINE
            )

        return text

    def _decode_quoted_printable(self, text: str) -> str:
        """Decode quoted-printable encoding if detected.

        Args:
            text: Text that may contain quoted-printable encoding

        Returns:
            Decoded text
        """
        # Check if quoted-printable encoding is present
        if not re.search(r"=\d{2}[A-Za-z0-9]", text):
            return text

        try:
            # Decode using quopri module
            decoded_bytes = quopri.decodestring(text.encode("latin-1"))
            decoded = decoded_bytes.decode("utf-8", errors="ignore")

            # Clean up common quoted-printable artifacts
            decoded = decoded.replace("=3D", "")
            decoded = decoded.replace("=2C", ",")
            decoded = decoded.replace("=E2=80=99", "'")
            decoded = decoded.replace("=E2=80=9C", '"')
            decoded = decoded.replace("=E2=80=9D", '"')
            decoded = decoded.replace("=0A", "\n")

            return decoded
        except Exception:
            # Return original if decoding fails
            return text

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized whitespace
        """
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
