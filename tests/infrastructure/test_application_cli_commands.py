"""Tests for CLI command registration and management."""

from unittest.mock import Mock, patch

import pytest

from src.application.services.booking_service import BookingService
from src.application.services.cancellation_service import CancellationService
from src.application.services.query_service import QueryService
from src.infrastructure.application import Application, ApplicationError
from src.infrastructure.cli.app import CLIApp
from src.infrastructure.config.models import ApplicationConfig
from src.infrastructure.container import ServiceContainer


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


def test_graceful_handling_when_services_not_registered():
    """Test graceful handling when required services are not registered in container."""
    app = Application()

    # Create a container without registering required services
    app.container = ServiceContainer()
    app.config = ApplicationConfig()
    app.cli_app = CLIApp()

    # Attempt to register commands should fail gracefully
    with pytest.raises(ApplicationError) as exc_info:
        app._register_cli_commands()

    assert "Failed to register CLI commands" in str(exc_info.value)
