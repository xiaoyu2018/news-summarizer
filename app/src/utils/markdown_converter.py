"""Markdown to HTML converter for email rendering."""

import markdown


class MarkdownConverter:
    """Utility class for converting Markdown to email-compatible HTML."""

    def __init__(self, extensions: list[str] | None = None):
        """Initialize converter with markdown extensions.

        Args:
            extensions: Optional list of markdown extensions to enable.
        """
        if extensions is None:
            extensions = ["extra", "nl2br", "sane_lists"]
        self._md = markdown.Markdown(extensions=extensions)

    def convert(self, markdown_text: str) -> str:
        """Convert Markdown to email-compatible HTML.

        Args:
            markdown_text: Markdown content to convert

        Returns:
            HTML formatted content with inline styles
        """
        if not markdown_text:
            return ""

        # Convert markdown to HTML
        html = self._md.convert(markdown_text)
        self._md.reset()

        # Wrap in email template with styles
        return self._wrap_in_email_template(html)

    def _wrap_in_email_template(self, html: str) -> str:
        """Wrap HTML content in email template with inline styles.

        Args:
            html: Raw HTML content

        Returns:
            Styled HTML email content
        """
        styles = (
            "font-family: Arial, sans-serif; font-size: 14px; "
            "line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto;"
        )

        header_styles = {
            "h1": "font-size: 24px; color: #2c3e50; margin-top: 20px; margin-bottom: 10px;",
            "h2": "font-size: 20px; color: #34495e; margin-top: 18px; margin-bottom: 8px;",
            "h3": "font-size: 18px; color: #7f8c8d; margin-top: 16px; margin-bottom: 6px;",
        }

        link_style = "color: #3498db; text-decoration: none;"
        list_style = "margin-left: 20px; margin-bottom: 10px;"
        li_style = "margin-bottom: 5px;"

        # Apply inline styles to elements
        html = html.replace("<h1", f'<h1 style="{header_styles["h1"]}"')
        html = html.replace("<h2", f'<h2 style="{header_styles["h2"]}"')
        html = html.replace("<h3", f'<h3 style="{header_styles["h3"]}"')
        html = html.replace("<a ", f'<a style="{link_style}" ')
        html = html.replace("<ul", f'<ul style="{list_style}"')
        html = html.replace("<ol", f'<ol style="{list_style}"')
        html = html.replace("<li>", f'<li style="{li_style}">')

        return f"""<!DOCTYPE html>
<html>
<body>
<div style="{styles}">
{html}
</div>
</body>
</html>"""


def convert_markdown(markdown_text: str) -> str:
    """Convenience function to convert Markdown to HTML.

    Args:
        markdown_text: Markdown content to convert

    Returns:
        HTML formatted content
    """
    converter = MarkdownConverter()
    return converter.convert(markdown_text)
