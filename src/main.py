"""Main entry point for news-summarizer."""

import sys
from datetime import datetime
from pathlib import Path

from src.collectors.email_collector import EmailCollector
from src.config_loader import ConfigLoader
from src.models import SourceItem
from src.processors.ai_processor import AIProcessor
from src.senders.email_sender import EmailSender
from src.utils.logger import setup_logger


class NewsSummarizer:
    """Main controller for the news summarization process."""

    def __init__(self, config_path: str = "conf/config.yaml"):
        """Initialize the news summarizer.

        Args:
            config_path: Path to configuration file
        """
        self.logger = setup_logger()
        self.config_path = config_path
        self.config: dict | None = None

    def run(self) -> None:
        """Run the news summarization process for all domains."""
        self.logger.info("Starting news-summarizer")

        try:
            self.config = self._load_config()
        except FileNotFoundError as e:
            self.logger.error(f"Configuration file not found: {e}")
            sys.exit(1)

        domains = self.config.get("domains", [])
        if not domains:
            self.logger.warning("No domains configured")
            return

        for domain in domains:
            self._process_domain(domain)

        self.logger.info("News summarization completed")

    def _load_config(self) -> dict:
        """Load configuration from file.

        Returns:
            Configuration dictionary
        """
        loader = ConfigLoader(self.config_path)
        return loader.load()

    def _process_domain(self, domain: dict) -> None:
        """Process a single domain.

        Args:
            domain: Domain configuration dictionary
        """
        domain_name = domain.get("name", "unknown")
        self.logger.info(f"Processing domain: {domain_name}")

        try:
            items = self._collect_items(domain)
            if not items:
                self.logger.warning(f"No items collected for domain {domain_name}")
                return

            processed_content = self._process_items(items, domain)
            if not processed_content:
                self.logger.error(f"Failed to process items for domain {domain_name}")
                return

            self._send_report(processed_content, domain)

        except Exception as e:
            self.logger.error(f"Error processing domain {domain_name}: {e}")

    def _collect_items(self, domain: dict) -> list[SourceItem]:
        """Collect items from all enabled collectors in domain.

        Args:
            domain: Domain configuration

        Returns:
            List of collected SourceItem objects
        """
        collectors_config = domain.get("collectors", [])
        if not collectors_config:
            self.logger.warning("No collectors configured")
            return []

        all_items: list[SourceItem] = []

        for collector_config in collectors_config:
            collector = self._create_collector(collector_config)
            if collector is None:
                continue

            try:
                self.logger.info(f"Running collector: {collector.name}")
                items = collector.collect()
                all_items.extend(items)
                self.logger.info(
                    f"Collector {collector.name} collected {len(items)} items"
                )
            except Exception as e:
                self.logger.error(f"Collector {collector.name} failed: {e}")

        return all_items

    def _create_collector(self, config: dict) -> EmailCollector | None:
        """Create a collector instance based on configuration.

        Args:
            config: Collector configuration

        Returns:
            Collector instance or None
        """
        collector_type = config.get("type", "")
        name = config.get("name", "unknown")

        if collector_type == "email":
            return EmailCollector(config, name)

        self.logger.warning(f"Unknown collector type: {collector_type}")
        return None

    def _process_items(self, items: list[SourceItem], domain: dict) -> str | None:
        """Process items using configured processor.

        Args:
            items: List of SourceItem objects
            domain: Domain configuration

        Returns:
            Processed content or None
        """
        processor_config = domain.get("processor", {})
        if not processor_config:
            self.logger.warning("No processor configured")
            return None

        processor = self._create_processor(processor_config)
        if processor is None:
            return None

        try:
            return processor.process(items)
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return None

    def _create_processor(self, config: dict) -> AIProcessor | None:
        """Create a processor instance based on configuration.

        Args:
            config: Processor configuration

        Returns:
            Processor instance or None
        """
        processor_type = config.get("type", "")
        name = config.get("name", "ai_processor")

        if processor_type == "ai":
            return AIProcessor(config, name)

        self.logger.warning(f"Unknown processor type: {processor_type}")
        return None

    def _send_report(self, content: str, domain: dict) -> bool:
        """Send report using configured sender.

        Args:
            content: Processed content to send
            domain: Domain configuration

        Returns:
            True if send was successful
        """
        sender_config = domain.get("sender", {})
        if not sender_config:
            self.logger.warning("No sender configured")
            return False

        sender = self._create_sender(sender_config)
        if sender is None:
            return False

        subject_prefix = sender_config.get("subject_prefix", "日报")
        date_str = datetime.now().strftime("%Y-%m-%d")
        subject = f"{subject_prefix} {date_str}"

        try:
            success = sender.send(content, subject)
            if success:
                self.logger.info(f"Report sent successfully: {subject}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to send report: {e}")
            return False

    def _create_sender(self, config: dict) -> EmailSender | None:
        """Create a sender instance based on configuration.

        Args:
            config: Sender configuration

        Returns:
            Sender instance or None
        """
        sender_type = config.get("type", "")
        name = config.get("name", "email_sender")

        if sender_type == "email":
            return EmailSender(config, name)

        self.logger.warning(f"Unknown sender type: {sender_type}")
        return None


def main():
    """Main entry point."""
    config_path = Path("conf/config.yaml")
    if not config_path.exists():
        config_path = Path(__file__).parent.parent / "conf" / "config.yaml"

    summarizer = NewsSummarizer(str(config_path))
    summarizer.run()


if __name__ == "__main__":
    main()
