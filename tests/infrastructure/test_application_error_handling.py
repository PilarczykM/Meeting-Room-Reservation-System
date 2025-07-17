"""Tests for application error handling."""

from unittest.mock import Mock, patch

import pytest

from src.infrastructure.application import Application, ApplicationError


def test_bootstrap_handles_configuration_error():
    """Test that bootstrap handles configuration errors gracefully."""
    app = Application()

    with patch("src.infrastructure.config.manager.ConfigurationManager.load_config") as mock_load:
        mock_load.side_effect = Exception("Configuration error")

        with pytest.raises(ApplicationError) as exc_info:
            app.bootstrap()

        # The error should be wrapped in a bootstrap failure message
        assert "Application bootstrap failed" in str(exc_info.value) or "Failed to load configuration" in str(
            exc_info.value
        )


def test_bootstrap_handles_service_configuration_error():
    """Test that bootstrap handles service configuration errors gracefully."""
    app = Application()

    with patch("src.infrastructure.service_configurator.ServiceConfigurator.configure_all") as mock_configure:
        mock_configure.side_effect = Exception("Service configuration error")

        with pytest.raises(ApplicationError) as exc_info:
            app.bootstrap()

        # The error should be wrapped in a bootstrap failure message
        assert "Application bootstrap failed" in str(exc_info.value) or "Failed to configure services" in str(
            exc_info.value
        )


def test_bootstrap_handles_logging_configuration_error():
    """Test that bootstrap handles logging configuration errors gracefully."""
    app = Application()

    with patch("logging.basicConfig") as mock_basic_config:
        mock_basic_config.side_effect = Exception("Logging configuration error")

        with pytest.raises(ApplicationError) as exc_info:
            app.bootstrap()

        # The error should be wrapped in a bootstrap failure message
        assert "Application bootstrap failed" in str(exc_info.value) or "Failed to configure logging" in str(
            exc_info.value
        )


def test_run_requires_bootstrap():
    """Test that run requires bootstrap to be called first."""
    app = Application()

    with pytest.raises(ApplicationError) as exc_info:
        app.run([])

    assert "Application not bootstrapped" in str(exc_info.value)


def test_run_handles_cli_errors():
    """Test that run handles CLI errors gracefully."""
    app = Application()
    app.bootstrap()

    mock_cli = Mock()
    mock_cli.run.side_effect = Exception("CLI error")
    app.cli_app = mock_cli

    with pytest.raises(ApplicationError) as exc_info:
        app.run([])

    assert "Application execution failed" in str(exc_info.value)


def test_application_error_with_details():
    """Test ApplicationError with details."""
    error = ApplicationError("Test error", {"component": "bootstrap"})

    assert error.message == "Test error"
    assert error.details == {"component": "bootstrap"}
    assert "Test error" in str(error)
    assert "bootstrap" in str(error)


def test_application_startup_fails_with_command_registration_error():
    """Test that application startup fails with clear error message if command registration fails."""
    app = Application()

    # Mock the command registration to fail
    with patch.object(app, "_register_cli_commands") as mock_register:
        mock_register.side_effect = Exception("Command registration failed")

        with pytest.raises(ApplicationError) as exc_info:
            app.bootstrap()

        assert "Application bootstrap failed" in str(exc_info.value)


def test_application_run_without_bootstrap_fails():
    """Test that running application without bootstrap fails gracefully."""
    app = Application()

    with pytest.raises(ApplicationError) as exc_info:
        app.run(["book"])

    assert "Application not bootstrapped" in str(exc_info.value)
