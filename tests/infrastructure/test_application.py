"""Tests for the application bootstrap system."""

import logging
from unittest.mock import Mock, patch

import pytest

from src.application.services.booking_service import BookingService
from src.application.services.cancellation_service import CancellationService
from src.application.services.query_service import QueryService
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.application import Application, ApplicationError
from src.infrastructure.cli.app import CLIApp
from src.infrastructure.config.models import ApplicationConfig, Environment
from src.infrastructure.container import ServiceContainer


def test_application_initialization():
    """Test that application can be initialized."""
    app = Application()

    assert app is not None
    assert app.container is None
    assert app.config is None
    assert app.cli_app is None


def test_application_initialization_with_config():
    """Test that application can be initialized with config."""
    config = ApplicationConfig()
    app = Application(config=config)

    assert app is not None
    assert app.config is config


def test_bootstrap_loads_configuration():
    """Test that bootstrap loads and validates configuration."""
    app = Application()

    app.bootstrap()

    assert app.config is not None
    assert isinstance(app.config, ApplicationConfig)


def test_bootstrap_creates_container():
    """Test that bootstrap creates dependency injection container."""
    app = Application()

    app.bootstrap()

    assert app.container is not None
    assert isinstance(app.container, ServiceContainer)


def test_bootstrap_configures_services():
    """Test that bootstrap configures all services."""
    app = Application()

    app.bootstrap()

    # Should be able to resolve services after bootstrap
    assert app.container is not None
    # Repository should be available as singleton

    repository = app.container.resolve(MeetingRoomRepository)
    assert repository is not None


def test_bootstrap_sets_up_logging():
    """Test that bootstrap sets up logging configuration."""
    app = Application()

    with patch("logging.basicConfig") as mock_basic_config:
        app.bootstrap()

        # Should have configured logging
        mock_basic_config.assert_called_once()


def test_bootstrap_creates_cli_app():
    """Test that bootstrap creates CLI application."""
    app = Application()

    app.bootstrap()

    assert app.cli_app is not None
    assert isinstance(app.cli_app, CLIApp)


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


def test_run_with_cli_arguments():
    """Test that run passes arguments to CLI application."""
    app = Application()
    app.bootstrap()

    mock_cli = Mock()
    app.cli_app = mock_cli

    args = ["book", "--room", "A", "--time", "10:00"]
    app.run(args)

    mock_cli.run.assert_called_once_with(args)


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


def test_shutdown_cleans_up_resources():
    """Test that shutdown cleans up resources properly."""
    app = Application()
    app.bootstrap()

    # Mock some resources
    mock_container = Mock()
    app.container = mock_container

    app.shutdown()

    # Should clean up resources
    assert app.container is None
    assert app.cli_app is None


def test_shutdown_handles_cleanup_errors():
    """Test that shutdown handles cleanup errors gracefully."""
    app = Application()
    app.bootstrap()

    # Mock container that raises error on cleanup
    mock_container = Mock()
    mock_container.cleanup = Mock(side_effect=Exception("Cleanup error"))
    app.container = mock_container

    # Should not raise exception
    app.shutdown()

    # Should still clean up what it can
    assert app.container is None


def test_application_error_with_details():
    """Test ApplicationError with details."""
    error = ApplicationError("Test error", {"component": "bootstrap"})

    assert error.message == "Test error"
    assert error.details == {"component": "bootstrap"}
    assert "Test error" in str(error)
    assert "bootstrap" in str(error)


def test_bootstrap_is_idempotent():
    """Test that calling bootstrap multiple times is safe."""
    app = Application()

    app.bootstrap()
    first_container = app.container
    first_config = app.config

    app.bootstrap()

    # Should not create new instances
    assert app.container is first_container
    assert app.config is first_config


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


# CLI Command Registration Tests (TDD)


def test_bootstrap_registers_cli_commands():
    """Test that bootstrap registers all CLI commands with the CLI application."""
    app = Application()
    app.bootstrap()

    # Verify CLI app has commands registered
    assert app.cli_app is not None
    assert "book" in app.cli_app.commands
    assert "cancel" in app.cli_app.commands
    assert "list" in app.cli_app.commands


def test_cli_commands_are_callable():
    """Test that registered CLI commands are callable."""
    app = Application()
    app.bootstrap()

    # All registered commands should be callable
    assert callable(app.cli_app.commands["book"])
    assert callable(app.cli_app.commands["cancel"])
    assert callable(app.cli_app.commands["list"])


def test_register_cli_commands_resolves_services():
    """Test that command registration resolves required services from container."""
    app = Application()
    app.bootstrap()

    # Mock the container to verify service resolution
    with patch.object(app.container, "create_scope") as mock_create_scope:
        mock_scope = Mock()
        mock_create_scope.return_value.__enter__.return_value = mock_scope

        # Mock service resolution
        mock_booking_service = Mock(spec=BookingService)
        mock_cancellation_service = Mock(spec=CancellationService)
        mock_query_service = Mock(spec=QueryService)

        mock_resolve = Mock()

        def resolve_side_effect(service_type):
            if service_type == BookingService:
                return mock_booking_service
            elif service_type == CancellationService:
                return mock_cancellation_service
            elif service_type == QueryService:
                return mock_query_service
            else:
                raise ValueError(f"Unexpected service type: {service_type}")

        mock_resolve.side_effect = resolve_side_effect
        mock_scope.resolve = mock_resolve

        # Re-register commands to test service resolution
        app._register_cli_commands()

        # Verify services were resolved
        mock_resolve.assert_any_call(BookingService)
        mock_resolve.assert_any_call(CancellationService)
        mock_resolve.assert_any_call(QueryService)


def test_register_cli_commands_handles_service_resolution_error():
    """Test that command registration handles service resolution errors gracefully."""
    app = Application()
    app.bootstrap()

    # Mock container to raise error during service resolution
    with patch.object(app.container, "create_scope") as mock_create_scope:
        mock_scope = Mock()
        mock_create_scope.return_value.__enter__.return_value = mock_scope
        mock_scope.resolve.side_effect = Exception("Service resolution failed")

        with pytest.raises(ApplicationError) as exc_info:
            app._register_cli_commands()

        assert "Failed to register CLI commands" in str(exc_info.value)


def test_register_booking_command():
    """Test that booking command is registered correctly."""
    app = Application()
    app.bootstrap()

    mock_booking_service = Mock(spec=BookingService)

    # Test individual command registration
    app._register_booking_command(mock_booking_service)

    # Verify command is registered
    assert "book" in app.cli_app.commands
    assert callable(app.cli_app.commands["book"])


def test_register_cancellation_command():
    """Test that cancellation command is registered correctly."""
    app = Application()
    app.bootstrap()

    mock_cancellation_service = Mock(spec=CancellationService)
    mock_query_service = Mock(spec=QueryService)

    # Test individual command registration
    app._register_cancellation_command(mock_cancellation_service, mock_query_service)

    # Verify command is registered
    assert "cancel" in app.cli_app.commands
    assert callable(app.cli_app.commands["cancel"])


def test_register_list_command():
    """Test that list command is registered correctly."""
    app = Application()
    app.bootstrap()

    mock_query_service = Mock(spec=QueryService)

    # Test individual command registration
    app._register_list_command(mock_query_service)

    # Verify command is registered
    assert "list" in app.cli_app.commands
    assert callable(app.cli_app.commands["list"])


def test_command_registration_creates_proper_handlers():
    """Test that command registration creates proper command handler instances."""
    app = Application()
    app.bootstrap()

    # Mock services
    mock_booking_service = Mock(spec=BookingService)
    mock_cancellation_service = Mock(spec=CancellationService)
    mock_query_service = Mock(spec=QueryService)

    # Mock command classes to verify they're instantiated correctly
    with (
        patch("src.infrastructure.application.BookingCommand") as mock_booking_cmd,
        patch("src.infrastructure.application.CancellationCommand") as mock_cancel_cmd,
        patch("src.infrastructure.application.ListCommand") as mock_list_cmd,
    ):
        mock_booking_instance = Mock()
        mock_cancel_instance = Mock()
        mock_list_instance = Mock()

        mock_booking_cmd.return_value = mock_booking_instance
        mock_cancel_cmd.return_value = mock_cancel_instance
        mock_list_cmd.return_value = mock_list_instance

        # Register commands
        app._register_booking_command(mock_booking_service)
        app._register_cancellation_command(mock_cancellation_service, mock_query_service)
        app._register_list_command(mock_query_service)

        # Verify command instances were created with correct services
        mock_booking_cmd.assert_called_once_with(mock_booking_service)
        mock_cancel_cmd.assert_called_once_with(mock_cancellation_service, mock_query_service)
        mock_list_cmd.assert_called_once_with(mock_query_service)
