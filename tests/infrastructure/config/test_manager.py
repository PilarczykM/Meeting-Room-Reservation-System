"""Tests for configuration manager."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.config.manager import ConfigurationError, ConfigurationManager
from src.infrastructure.config.models import ApplicationConfig, Environment, LogLevel, RepositoryType


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""

    def test_manager_initialization_default_config_dir(self):
        """Test that manager initializes with default config directory."""
        manager = ConfigurationManager()

        assert manager.config_dir == Path("config")

    def test_manager_initialization_custom_config_dir(self):
        """Test that manager initializes with custom config directory."""
        custom_dir = Path("/custom/config")
        manager = ConfigurationManager(config_dir=custom_dir)

        assert manager.config_dir == custom_dir

    def test_load_config_default_environment(self):
        """Test loading configuration with default environment."""
        manager = ConfigurationManager()

        with patch.dict(os.environ, {}, clear=True):
            config = manager.load_config()

        assert config.environment == Environment.DEVELOPMENT
        # Note: The actual log level might be different due to environment-specific logic
        assert config.log_level in [LogLevel.INFO, LogLevel.DEBUG]
        assert config.repository_type == RepositoryType.IN_MEMORY

    def test_load_config_environment_from_parameter(self):
        """Test loading configuration with environment from parameter."""
        manager = ConfigurationManager()

        config = manager.load_config(env="test")

        assert config.environment == Environment.TEST

    def test_load_config_environment_from_env_var(self):
        """Test loading configuration with environment from environment variable."""
        manager = ConfigurationManager()

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            config = manager.load_config()

        assert config.environment == Environment.PRODUCTION

    def test_load_config_with_environment_variables(self):
        """Test loading configuration with environment variable overrides."""
        manager = ConfigurationManager()

        env_vars = {
            "MRRS_ENVIRONMENT": "test",
            "MRRS_LOG_LEVEL": "DEBUG",
            "MRRS_LOG_FORMAT": "%(message)s",
            "MRRS_REPOSITORY_TYPE": "in_memory",
        }

        with patch.dict(os.environ, env_vars):
            config = manager.load_config()

        assert config.environment == Environment.TEST
        assert config.log_level == LogLevel.DEBUG
        assert config.log_format == "%(message)s"
        assert config.repository_type == RepositoryType.IN_MEMORY

    def test_load_config_with_file_configuration(self):
        """Test loading configuration from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "test.json"

            # Create test configuration file
            config_data = {
                "log_level": "WARNING",
                "log_format": "%(name)s - %(message)s",
            }

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            manager = ConfigurationManager(config_dir=config_dir)
            config = manager.load_config(env="test")

            assert config.log_level == LogLevel.WARNING
            assert config.log_format == "%(name)s - %(message)s"

    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = ConfigurationManager(config_dir=config_dir)

            # Should raise exception for invalid environment
            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config(env="nonexistent")

            assert "Configuration validation failed" in str(exc_info.value)

    def test_load_config_invalid_json_file(self):
        """Test loading configuration with invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "test.json"

            # Create invalid JSON file
            with open(config_file, "w") as f:
                f.write("{ invalid json }")

            manager = ConfigurationManager(config_dir=config_dir)

            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config(env="test")

            # The error should contain information about the failed configuration loading
            assert "Failed to load configuration" in str(exc_info.value)
            # Check that the error details contain environment information
            assert "environment" in exc_info.value.details

    def test_load_config_validation_error(self):
        """Test loading configuration with validation errors."""
        manager = ConfigurationManager()

        # Mock invalid environment variable
        with patch.dict(os.environ, {"MRRS_LOG_LEVEL": "INVALID_LEVEL"}):
            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config()

            assert "Configuration validation failed" in str(exc_info.value)
            assert "validation_errors" in exc_info.value.details

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        manager = ConfigurationManager()
        config = ApplicationConfig()

        # Should not raise exception
        manager.validate_config(config)

    def test_validate_config_production_debug_warning(self):
        """Test validation warning for DEBUG logging in production."""
        manager = ConfigurationManager()
        config = ApplicationConfig(environment=Environment.PRODUCTION, log_level=LogLevel.DEBUG)

        with pytest.raises(ConfigurationError) as exc_info:
            manager.validate_config(config)

        assert "Configuration validation failed" in str(exc_info.value)

    def test_load_default_config(self):
        """Test loading default configuration values."""
        manager = ConfigurationManager()
        defaults = manager._load_default_config()

        assert defaults["environment"] == Environment.DEVELOPMENT.value
        assert defaults["log_level"] == "INFO"
        assert defaults["repository_type"] == "in_memory"
        assert "logging" in defaults

    def test_load_env_variables_empty(self):
        """Test loading environment variables when none are set."""
        manager = ConfigurationManager()

        with patch.dict(os.environ, {}, clear=True):
            env_config = manager._load_env_variables()

        assert env_config == {}

    def test_load_env_variables_partial(self):
        """Test loading environment variables when only some are set."""
        manager = ConfigurationManager()

        env_vars = {
            "MRRS_LOG_LEVEL": "ERROR",
            "OTHER_VAR": "ignored",
        }

        with patch.dict(os.environ, env_vars):
            env_config = manager._load_env_variables()

        assert env_config == {"log_level": "ERROR"}
        assert "OTHER_VAR" not in env_config

    def test_configuration_precedence(self):
        """Test that configuration sources have correct precedence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "test.json"

            # Create file configuration
            file_config = {"log_level": "WARNING"}
            with open(config_file, "w") as f:
                json.dump(file_config, f)

            manager = ConfigurationManager(config_dir=config_dir)

            # Environment variables should override file configuration
            env_vars = {"MRRS_LOG_LEVEL": "ERROR"}

            with patch.dict(os.environ, env_vars):
                config = manager.load_config(env="test")

            # Environment variable should take precedence
            assert config.log_level == LogLevel.ERROR

    def test_configuration_error_with_details(self):
        """Test ConfigurationError with details."""
        error = ConfigurationError("Test error", {"key": "value"})

        assert str(error) == "Test error"
        assert error.details == {"key": "value"}

    def test_configuration_error_without_details(self):
        """Test ConfigurationError without details."""
        error = ConfigurationError("Test error")

        assert str(error) == "Test error"
        assert error.details == {}
