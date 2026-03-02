"""Email sender using SMTP."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.src.senders.base import Sender
from app.src.utils.markdown_converter import convert_markdown


class EmailSender(Sender):
    """Sender that sends emails via SMTP."""

    def __init__(self, config: dict[str, Any], name: str):
        """Initialize the email sender.

        Args:
            config: Sender configuration with SMTP settings
            name: Unique name for this sender instance
        """
        super().__init__(config, name)
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 465)
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
        self.receiver_email = config.get("receiver_email", "")
        self.use_tls = config.get("use_tls", False)

    def send(self, content: str, subject: str) -> bool:
        """Send email via SMTP.

        Args:
            content: Email body content
            subject: Email subject line

        Returns:
            True if send was successful
        """
        self.logger.info(f"Sending email to {self.receiver_email}")

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.receiver_email

            text_part = MIMEText(content, "plain", "utf-8")
            html_part = MIMEText(self._convert_to_html(content), "html", "utf-8")

            message.attach(text_part)
            message.attach(html_part)

            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(
                        self.sender_email, self.receiver_email, message.as_string()
                    )
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(
                        self.sender_email, self.receiver_email, message.as_string()
                    )

            self.logger.info("Email sent successfully")
            return True

        except smtplib.SMTPException as e:
            self.logger.exception(f"Failed to send email: {e}")
            return False

    def _convert_to_html(self, content: str) -> str:
        """Convert Markdown content to email-compatible HTML.

        Args:
            content: Markdown content to convert

        Returns:
            HTML formatted content
        """
        return convert_markdown(content)
