"""Tests for application bootstrap functionality."""

from unittest.mock import patch

from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.application import Application
from src.infrastructure.cli.app import CLIApp
from src.infrastructure.config.models import ApplicationConfig
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
