"""AI-powered processor using OpenAI-compatible APIs."""

from pathlib import Path
from typing import Any

from openai import APIConnectionError, APIError, OpenAI, RateLimitError

from app.src.models import SourceItem
from app.src.processors.base import Processor


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
        # AI model parameters
        self.enable_thinking = config.get(
            "enable_thinking", True
        )  # Enable thinking mode for GLM-4.7
        self.max_tokens = config.get("max_tokens", 131072)  # Max output tokens
        self.temperature = config.get("temperature", 0.7)  # Control randomness (0-1)
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

        # Use prompt as system_message, combined content as user_message
        system_prompt = prompt_template
        user_prompt = combined_content

        self.logger.debug(f"System prompt length: {len(system_prompt)} characters")
        self.logger.debug(f"User prompt length: {len(user_prompt)} characters")

        try:
            # Build API parameters with separated messages
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            # GLM-4.7 thinking mode requires extra_body parameter
            if self.enable_thinking and self.provider.upper() == "ZHIPUAI":
                api_params["extra_body"] = {"thinking": {"type": "enabled"}}

            response = self.client.chat.completions.create(**api_params)

            summary = response.choices[0].message.content
            summary = self._strip_code_block(summary)
            self.logger.info("AI processing completed successfully")
            return summary or "生成摘要失败。"

        except (APIError, APIConnectionError, RateLimitError) as e:
            self.logger.exception(f"AI processing failed: {e}")
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
            combined.append(f"--- 来源 {i} ---\n{item.to_str()}")

        return "\n".join(combined)

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

    @staticmethod
    def _strip_code_block(content: str) -> str:
        """Remove markdown code block wrapper from AI output.

        AI models often wrap output in ```markdown ... ``` when the prompt
        contains code blocks. This strips that wrapper.

        Args:
            content: AI-generated content that may be wrapped in code block

        Returns:
            Content with code block wrapper removed
        """
        content = content.strip()

        # Check if content starts with ```markdown or ``` and ends with ```
        if content.startswith("```markdown\n"):
            content = content[len("```markdown\n") :]
        elif content.startswith("```\n"):
            content = content[len("```\n") :]

        if content.endswith("\n```"):
            content = content[: -len("\n```")]
        elif content.endswith("```"):
            content = content[: -len("```")]

        return content.strip()
