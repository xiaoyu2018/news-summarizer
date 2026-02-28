"""Main entry point for news-summarizer."""

from pathlib import Path

from app.src.summarizer import NewsSummarizer


def main():
    """Main entry point."""
    config_path = Path("app/conf/config.yaml")
    if not config_path.exists():
        config_path = (
            Path(__file__).parent.parent.parent / "app" / "conf" / "config.yaml"
        )

    summarizer = NewsSummarizer(str(config_path))
    summarizer.run()


if __name__ == "__main__":
    main()
