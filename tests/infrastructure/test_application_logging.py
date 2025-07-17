"""Tests for application logging configuration."""

import logging
from unittest.mock import patch

from src.infrastructure.application import Application
from src.infrastructure.config.models import ApplicationConfig, Environment


def test_bootstrap_with_development_environment():
    """Test bootstrap with development environment configuration."""
    config = ApplicationConfig(environment=Environment.DEVELOPMENT)
    app = Application(config=config)

    with patch("logging.basicConfig") as mock_basic_config:
        app.bootstrap()

        # Should configure logging for development
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        assert kwargs.get("level") == logging.DEBUG


def test_bootstrap_with_test_environment():
    """Test bootstrap with test environment configuration."""
    config = ApplicationConfig(environment=Environment.TEST)
    app = Application(config=config)

    with patch("logging.basicConfig") as mock_basic_config:
        app.bootstrap()

        # Should configure logging for test
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        assert kwargs.get("level") == logging.WARNING


def test_bootstrap_with_production_environment():
    """Test bootstrap with production environment configuration."""
    config = ApplicationConfig(environment=Environment.PRODUCTION)
    app = Application(config=config)

    with patch("logging.basicConfig") as mock_basic_config:
        app.bootstrap()

        # Should configure logging for production
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        assert kwargs.get("level") == logging.INFO


def test_get_logging_level_for_environment():
    """Test that correct logging level is returned for environment."""
    app = Application()

    assert app._get_logging_level(Environment.DEVELOPMENT) == logging.DEBUG
    assert app._get_logging_level(Environment.TEST) == logging.WARNING
    assert app._get_logging_level(Environment.PRODUCTION) == logging.INFO


def test_configure_logging_with_custom_format():
    """Test that logging is configured with custom format."""
    config = ApplicationConfig(log_format="%(name)s - %(message)s")
    app = Application(config=config)

    with patch("logging.basicConfig") as mock_basic_config:
        app.bootstrap()

        args, kwargs = mock_basic_config.call_args
        assert kwargs.get("format") == "%(name)s - %(message)s"
