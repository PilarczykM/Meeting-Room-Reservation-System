"""Configuration manager for loading and validating application settings."""

import json
import os
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.infrastructure.config.models import ApplicationConfig, Environment


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class ConfigurationManager:
    """Manages application configuration loading from multiple sources."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files.
                       Defaults to 'config' in project root.

        """
        self.config_dir = config_dir or Path("config")

    def load_config(self, env: str | None = None) -> ApplicationConfig:
        """Load configuration from multiple sources with precedence.

        Configuration sources in order of precedence:
        1. Environment variables
        2. Configuration files (config/{env}.json)
        3. Default values

        Args:
            env: Environment name. If None, uses ENVIRONMENT env var or 'development'

        Returns:
            Validated ApplicationConfig instance

        Raises:
            ConfigurationError: If configuration loading or validation fails

        """
        try:
            # Determine environment
            environment = env or os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)

            # Load base configuration
            config_data = self._load_default_config()
            config_data["environment"] = environment

            # Load environment-specific configuration file
            file_config = self._load_config_file(environment)
            if file_config:
                config_data.update(file_config)

            # Override with environment variables
            env_config = self._load_env_variables()
            config_data.update(env_config)

            # Validate and create configuration
            return ApplicationConfig(**config_data)

        except ValidationError as e:
            raise ConfigurationError(
                f"Configuration validation failed: {e}", details={"validation_errors": e.errors()}
            ) from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}", details={"environment": environment}) from e

    def validate_config(self, config: ApplicationConfig) -> None:
        """Validate configuration for consistency and completeness.

        Args:
            config: Configuration to validate

        Raises:
            ConfigurationError: If validation fails

        """

        def _validate_production_config():
            if config.environment == Environment.PRODUCTION:
                if config.log_level == "DEBUG":
                    raise ValueError("DEBUG logging not recommended for production")

        try:
            # Re-validate using Pydantic
            config.dict()

            # Additional business logic validation
            _validate_production_config()

        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}", details={"config": config.dict()}) from e

    def _load_default_config(self) -> dict[str, Any]:
        """Load default configuration values."""
        return {
            "environment": Environment.DEVELOPMENT.value,
            "log_level": "INFO",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "repository_type": "in_memory",
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "handlers": ["console"],
            },
        }

    def _load_config_file(self, environment: str) -> dict[str, Any] | None:
        """Load configuration from environment-specific file.

        Args:
            environment: Environment name

        Returns:
            Configuration dictionary or None if file doesn't exist

        """
        config_file = self.config_dir / f"{environment}.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise ConfigurationError(
                f"Failed to load configuration file {config_file}: {e}", details={"file": str(config_file)}
            ) from e

    def _load_env_variables(self) -> dict[str, Any]:
        """Load configuration from environment variables.

        Environment variables are prefixed with 'MRRS_' (Meeting Room Reservation System).

        Returns:
            Configuration dictionary from environment variables

        """
        config = {}

        # Map environment variables to config keys
        env_mappings = {
            "MRRS_ENVIRONMENT": "environment",
            "MRRS_LOG_LEVEL": "log_level",
            "MRRS_LOG_FORMAT": "log_format",
            "MRRS_REPOSITORY_TYPE": "repository_type",
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                config[config_key] = value

        return config
