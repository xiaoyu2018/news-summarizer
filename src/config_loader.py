"""Configuration loader with environment variable resolution."""

import os
import re
from pathlib import Path
from typing import Any

import yaml

ENV_VAR_PATTERN = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


class ConfigLoader:
    """Loads YAML configuration and resolves environment variable placeholders."""

    def __init__(self, config_path: str | Path = "config.yaml"):
        """Initialize the config loader.

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        """Load and parse the configuration file.

        Returns:
            Parsed configuration with resolved environment variables
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        self._config = self._resolve_env_vars(raw_config)
        return self._config

    def _resolve_env_vars(self, obj: Any) -> Any:
        """Recursively resolve environment variable placeholders.

        Args:
            obj: Object to resolve (can be dict, list, str, or other)

        Returns:
            Object with environment variables resolved
        """
        if isinstance(obj, dict):
            return {k: self._resolve_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._resolve_string(obj)
        return obj

    def _resolve_string(self, value: str) -> str:
        """Resolve environment variable placeholders in a string.

        Args:
            value: String potentially containing ${ENV_VAR} placeholders

        Returns:
            String with resolved environment variables
        """

        def replace_env_var(match: re.Match) -> str:
            var_name = match.group(1)
            env_value = os.environ.get(var_name)
            if env_value is None:
                return match.group(0)
            return env_value

        return ENV_VAR_PATTERN.sub(replace_env_var, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (supports dot notation like "global.timezone")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    @property
    def config(self) -> dict[str, Any]:
        """Get the loaded configuration."""
        return self._config


def load_config(config_path: str | Path = "config.yaml") -> dict[str, Any]:
    """Convenience function to load configuration.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Parsed configuration with resolved environment variables
    """
    loader = ConfigLoader(config_path)
    return loader.load()
