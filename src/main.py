"""Main entry point for news-summarizer."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.summarizer import NewsSummarizer

def main():
    """Main entry point."""
    config_path = Path("conf/config.yaml")
    if not config_path.exists():
        config_path = Path(__file__).parent.parent / "conf" / "config.yaml"

    summarizer = NewsSummarizer(str(config_path))
    summarizer.run()


if __name__ == "__main__":
    main()
