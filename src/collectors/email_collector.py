"""Email collector using IMAP."""

import email
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import Message
from typing import Any

import imaplib

from src.collectors.base import Collector
from src.models import SourceItem
from src.utils.html_cleaner import HTMLCleaner


class EmailCollector(Collector):
    """Collector that reads emails from an IMAP mailbox."""

    def __init__(self, config: dict[str, Any], name: str):
        """Initialize the email collector.

        Args:
            config: Collector configuration with IMAP settings
            name: Unique name for this collector instance
        """
        super().__init__(config, name)
        self.imap_server = config.get("imap_server", "imap.gmail.com")
        self.email_account = config.get("email_account", "")
        self.email_password = config.get("email_password", "")
        self.mailbox = config.get("mailbox", "INBOX")
        self.mark_as_seen = config.get("mark_as_seen", True)
        self.time_range_days = config.get("time_range_days", 1)

    def collect(self) -> list[SourceItem]:
        """Collect unread emails from the configured mailbox.

        Returns:
            List of SourceItem objects
        """
        self.logger.info(f"Starting email collection from {self.email_account}")

        items: list[SourceItem] = []

        try:
            with self._connect() as mail:
                status, _ = mail.select(self.mailbox)
                if status != "OK":
                    self.logger.error(
                        f"Failed to select mailbox '{self.mailbox}': {status}"
                    )
                    return items

                search_criteria = self._build_search_criteria()
                self.logger.debug(f"Search criteria: {search_criteria}")

                _, message_ids = mail.search(None, search_criteria)
                message_id_list = message_ids[0].split()

                self.logger.info(f"Found {len(message_id_list)} emails to process")

                for msg_id in message_id_list:
                    try:
                        item = self._process_email(mail, msg_id)
                        if item:
                            items.append(item)

                            if not self.mark_as_seen:
                                mail.store(msg_id, "-FLAGS", "\\Seen")
                    except Exception as e:
                        self.logger.error(f"Error processing email {msg_id}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to collect emails: {e}")

        self.logger.info(f"Collected {len(items)} items from email")
        return items

    def _connect(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server.

        Returns:
            IMAP connection
        """
        self.logger.debug(f"Connecting to {self.imap_server}")
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_account, self.email_password)
        return mail

    def _build_search_criteria(self) -> str:
        """Build IMAP search criteria.

        Returns:
            Search criteria string
        """
        since_date = (datetime.now() - timedelta(days=self.time_range_days)).strftime(
            "%d-%b-%Y"
        )
        return f'(UNSEEN SINCE "{since_date}")'

    def _process_email(
        self, mail: imaplib.IMAP4_SSL, msg_id: bytes
    ) -> SourceItem | None:
        """Process a single email message.

        Args:
            mail: IMAP connection
            msg_id: Message ID

        Returns:
            SourceItem or None if processing fails
        """
        _, msg_data = mail.fetch(msg_id, "(RFC822)")

        if not msg_data or not msg_data[0]:
            return None

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = self._decode_header(msg.get("Subject", "No Subject"))
        sender = self._extract_sender(msg)
        content = self._extract_content(msg)
        timestamp = self._extract_timestamp(msg)
        urls = self._extract_urls(content)

        if not content.strip():
            self.logger.debug(f"Skipping email with empty content: {subject}")
            return None

        source_id = f"{self.email_account}:{msg_id.decode()}"

        return SourceItem(
            source_type="email",
            source_id=source_id,
            title=subject,
            content=content,
            url=urls[0] if urls else None,
            timestamp=timestamp,
            raw_data={"sender": sender, "subject": subject},
        )

    @staticmethod
    def _decode_header(header_value: str) -> str:
        """Decode email header value.

        Args:
            header_value: Raw header value

        Returns:
            Decoded string
        """
        if not header_value:
            return "No Subject"

        decoded_parts = decode_header(header_value)
        result = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result += part.decode(encoding or "utf-8", errors="ignore")
            else:
                result += part
        return result.strip()

    def _extract_sender(self, msg: Message) -> str:
        """Extract sender from email message.

        Args:
            msg: Email message

        Returns:
            Sender email address
        """
        from_header = msg.get("From", "")
        if "<" in from_header:
            return from_header.split("<")[1].strip(">")
        return from_header.strip()

    def _extract_content(self, msg: Message) -> str:
        """Extract content from email message.

        Args:
            msg: Email message

        Returns:
            Extracted text content
        """
        cleaner = HTMLCleaner()

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        return cleaner.clean(payload.decode(charset, errors="ignore"))
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        return cleaner.clean(payload.decode(charset, errors="ignore"))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                return cleaner.clean(payload.decode(charset, errors="ignore"))

        return ""

    def _extract_timestamp(self, msg: Message) -> datetime | None:
        """Extract timestamp from email message.

        Args:
            msg: Email message

        Returns:
            Datetime object or None
        """
        date_str = msg.get("Date", "")
        if not date_str:
            return None

        try:
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def _extract_urls(self, content: str) -> list[str]:
        """Extract URLs from content.

        Args:
            content: Text content

        Returns:
            List of URLs
        """
        import re

        url_pattern = re.compile(
            r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*",
            re.IGNORECASE,
        )
        return list(set(url_pattern.findall(content)))[:5]
