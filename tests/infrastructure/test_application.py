"""Tests for the application bootstrap system."""

import logging
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.application import Application, ApplicationError
from src.infrastructure.cli.app import CLIApp
from src.infrastructure.config.models import ApplicationConfig, Environment
from src.infrastructure.container import ServiceContainer


class TestApplication:
    """Test cases for Application bootstrap system."""

    def test_application_initialization(self):
        """Test that application can be initialized."""
        app = Application()

        assert app is not None
        assert app.container is None
        assert app.config is None
        assert app.cli_app is None

    def test_application_initialization_with_config(self):
        """Test that application can be initialized with config."""
        config = ApplicationConfig()
        app = Application(config=config)

        assert app is not None
        assert app.config is config

    def test_bootstrap_loads_configuration(self):
        """Test that bootstrap loads and validates configuration."""
        app = Application()

        app.bootstrap()

        assert app.config is not None
        assert isinstance(app.config, ApplicationConfig)

    def test_bootstrap_creates_container(self):
        """Test that bootstrap creates dependency injection container."""
        app = Application()

        app.bootstrap()

        assert app.container is not None
        assert isinstance(app.container, ServiceContainer)

    def test_bootstrap_configures_services(self):
        """Test that bootstrap configures all services."""
        app = Application()

        app.bootstrap()

        # Should be able to resolve services after bootstrap
        assert app.container is not None
        # Repository should be available as singleton
        from src.domain.repositories.meeting_room_repository import MeetingRoomRepository

        repository = app.container.resolve(MeetingRoomRepository)
        assert repository is not None

    def test_bootstrap_sets_up_logging(self):
        """Test that bootstrap sets up logging configuration."""
        app = Application()

        with patch("logging.basicConfig") as mock_basic_config:
            app.bootstrap()

            # Should have configured logging
            mock_basic_config.assert_called_once()

    def test_bootstrap_creates_cli_app(self):
        """Test that bootstrap creates CLI application."""
        app = Application()

        app.bootstrap()

        assert app.cli_app is not None
        assert isinstance(app.cli_app, CLIApp)

    def test_bootstrap_with_development_environment(self):
        """Test bootstrap with development environment configuration."""
        config = ApplicationConfig(environment=Environment.DEVELOPMENT)
        app = Application(config=config)

        with patch("logging.basicConfig") as mock_basic_config:
            app.bootstrap()

            # Should configure logging for development
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs.get("level") == logging.DEBUG

    def test_bootstrap_with_test_environment(self):
        """Test bootstrap with test environment configuration."""
        config = ApplicationConfig(environment=Environment.TEST)
        app = Application(config=config)

        with patch("logging.basicConfig") as mock_basic_config:
            app.bootstrap()

            # Should configure logging for test
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs.get("level") == logging.WARNING

    def test_bootstrap_with_production_environment(self):
        """Test bootstrap with production environment configuration."""
        config = ApplicationConfig(environment=Environment.PRODUCTION)
        app = Application(config=config)

        with patch("logging.basicConfig") as mock_basic_config:
            app.bootstrap()

            # Should configure logging for production
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs.get("level") == logging.INFO

    def test_bootstrap_handles_configuration_error(self):
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

    def test_bootstrap_handles_service_configuration_error(self):
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

    def test_bootstrap_handles_logging_configuration_error(self):
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

    def test_run_requires_bootstrap(self):
        """Test that run requires bootstrap to be called first."""
        app = Application()

        with pytest.raises(ApplicationError) as exc_info:
            app.run([])

        assert "Application not bootstrapped" in str(exc_info.value)

    def test_run_with_cli_arguments(self):
        """Test that run passes arguments to CLI application."""
        app = Application()
        app.bootstrap()

        mock_cli = Mock()
        app.cli_app = mock_cli

        args = ["book", "--room", "A", "--time", "10:00"]
        app.run(args)

        mock_cli.run.assert_called_once_with(args)

    def test_run_handles_cli_errors(self):
        """Test that run handles CLI errors gracefully."""
        app = Application()
        app.bootstrap()

        mock_cli = Mock()
        mock_cli.run.side_effect = Exception("CLI error")
        app.cli_app = mock_cli

        with pytest.raises(ApplicationError) as exc_info:
            app.run([])

        assert "Application execution failed" in str(exc_info.value)

    def test_shutdown_cleans_up_resources(self):
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

    def test_shutdown_handles_cleanup_errors(self):
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

    def test_application_error_with_details(self):
        """Test ApplicationError with details."""
        error = ApplicationError("Test error", {"component": "bootstrap"})

        assert error.message == "Test error"
        assert error.details == {"component": "bootstrap"}
        assert "Test error" in str(error)
        assert "bootstrap" in str(error)

    def test_bootstrap_is_idempotent(self):
        """Test that calling bootstrap multiple times is safe."""
        app = Application()

        app.bootstrap()
        first_container = app.container
        first_config = app.config

        app.bootstrap()

        # Should not create new instances
        assert app.container is first_container
        assert app.config is first_config

    def test_get_logging_level_for_environment(self):
        """Test that correct logging level is returned for environment."""
        app = Application()

        assert app._get_logging_level(Environment.DEVELOPMENT) == logging.DEBUG
        assert app._get_logging_level(Environment.TEST) == logging.WARNING
        assert app._get_logging_level(Environment.PRODUCTION) == logging.INFO

    def test_configure_logging_with_custom_format(self):
        """Test that logging is configured with custom format."""
        config = ApplicationConfig(log_format="%(name)s - %(message)s")
        app = Application(config=config)

        with patch("logging.basicConfig") as mock_basic_config:
            app.bootstrap()

            args, kwargs = mock_basic_config.call_args
            assert kwargs.get("format") == "%(name)s - %(message)s"
