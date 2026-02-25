"""AI-powered processor using OpenAI-compatible APIs."""

from pathlib import Path
from typing import Any

from openai import APIConnectionError, APIError, OpenAI, RateLimitError

from src.models import SourceItem
from src.processors.base import Processor


class AIProcessor(Processor):
    """Processor that uses AI to generate summaries."""

    def __init__(self, config: dict[str, Any], name: str):
        """Initialize the AI processor.

        Args:
            config: Processor configuration with AI settings
            name: Unique name for this processor instance
        """
        super().__init__(config, name)
        self.provider = config.get("provider", "openai")
        self.api_base = config.get("api_base", "https://api.openai.com/v1")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-4")
        self.prompt_file = config.get("prompt_file", "")
        self._client: OpenAI | None = None
        self._prompt_template: str | None = None

    @property
    def client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        return self._client

    def process(self, items: list[SourceItem]) -> str:
        """Process source items using AI.

        Args:
            items: List of SourceItem objects

        Returns:
            AI-generated summary
        """
        self.logger.info(f"Processing {len(items)} items with AI")

        if not items:
            self.logger.warning("No items to process")
            return "今日无新闻内容。"

        prompt_template = self._load_prompt()
        combined_content = self._combine_items(items)
        prompt = prompt_template.replace("{combined_content}", combined_content)

        self.logger.debug(f"Prompt length: {len(prompt)} characters")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional news editor.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
            )

            summary = response.choices[0].message.content
            self.logger.info("AI processing completed successfully")
            return summary or "生成摘要失败。"

        except (APIError, APIConnectionError, RateLimitError) as e:
            self.logger.error(f"AI processing failed: {e}")
            return f"AI处理失败: {str(e)}"

    def _load_prompt(self) -> str:
        """Load prompt template from file.

        Returns:
            Prompt template string
        """
        if self._prompt_template is not None:
            return self._prompt_template

        if not self.prompt_file:
            self.logger.warning("No prompt_file configured, using default")
            self._prompt_template = self._get_default_prompt()
            return self._prompt_template

        prompt_path = Path(self.prompt_file)
        if not prompt_path.is_absolute():
            prompt_path = Path.cwd() / prompt_path

        if not prompt_path.exists():
            self.logger.warning(f"Prompt file not found: {prompt_path}, using default")
            self._prompt_template = self._get_default_prompt()
            return self._prompt_template

        try:
            self._prompt_template = prompt_path.read_text(encoding="utf-8")
            self.logger.debug(f"Loaded prompt from {prompt_path}")
            return self._prompt_template
        except OSError as e:
            self.logger.warning(
                f"Failed to read prompt file: {prompt_path}, using default: {e}"
            )
            self._prompt_template = self._get_default_prompt()
            return self._prompt_template

    @staticmethod
    def _combine_items(items: list[SourceItem]) -> str:
        """Combine source items into formatted content.

        Args:
            items: List of SourceItem objects

        Returns:
            Combined content string
        """
        combined = []
        for i, item in enumerate(items, 1):
            source_info = f"来源: {item.source_type}"
            if item.url:
                source_info += f" | 链接: {item.url}"

            combined.append(
                f"--- 新闻 {i} ---\n"
                f"标题: {item.title}\n"
                f"{source_info}\n"
                f"内容: {item.content[:1000]}"
            )

        return "\n\n".join(combined)

    @staticmethod
    def _get_default_prompt() -> str:
        """Get default prompt template.

        Returns:
            Default prompt string
        """
        return """请根据以下新闻内容，整理一份今日摘要。

要求：
- 提取最重要的新闻
- 去除重复内容
- 每条新闻提供核心摘要

新闻内容：
{combined_content}

今日摘要："""
