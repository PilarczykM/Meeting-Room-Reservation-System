"""Application bootstrap system for coordinating startup sequence."""

import logging
from typing import Any

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.config.manager import ConfigurationError, ConfigurationManager
from src.infrastructure.config.models import ApplicationConfig, Environment
from src.infrastructure.container import ServiceContainer
from src.infrastructure.service_configurator import ServiceConfigurator


class ApplicationError(Exception):
    """Raised when application bootstrap or execution fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}


class Application:
    """Main application class that coordinates startup sequence."""

    def __init__(self, config: ApplicationConfig | None = None):
        """Initialize the application.

        Args:
            config: Optional pre-loaded configuration

        """
        self.config = config
        self.container: ServiceContainer | None = None
        self.cli_app: CLIApp | None = None
        self._bootstrapped = False

    def bootstrap(self) -> None:
        """Bootstrap the application with configuration, services, and logging."""
        if self._bootstrapped:
            return  # Idempotent - safe to call multiple times

        try:
            # Load configuration if not provided
            if self.config is None:
                self._load_configuration()

            # Set up logging
            self._configure_logging()

            # Create and configure dependency injection container
            self._create_container()
            self._configure_services()

            # Create CLI application
            self._create_cli_app()

            self._bootstrapped = True

        except ConfigurationError as e:
            raise ApplicationError(f"Failed to load configuration: {e}", details=e.details) from e
        except Exception as e:
            if "configure services" in str(e):
                raise ApplicationError(f"Failed to configure services: {e}") from e
            elif "configure logging" in str(e):
                raise ApplicationError(f"Failed to configure logging: {e}") from e
            else:
                raise ApplicationError(f"Application bootstrap failed: {e}") from e

    def run(self, args: list[str]) -> None:
        """Run the application with the given arguments.

        Args:
            args: Command-line arguments

        Raises:
            ApplicationError: If application is not bootstrapped or execution fails

        """
        if not self._bootstrapped:
            raise ApplicationError("Application not bootstrapped. Call bootstrap() first.")

        try:
            self.cli_app.run(args)
        except Exception as e:
            raise ApplicationError(f"Application execution failed: {e}") from e

    def shutdown(self) -> None:
        """Shutdown the application and clean up resources."""
        try:
            # Clean up container resources
            if self.container and hasattr(self.container, "cleanup"):
                try:
                    self.container.cleanup()
                except Exception:
                    # Log error but continue cleanup
                    pass

            # Clean up references
            self.container = None
            self.cli_app = None

        except Exception:
            # Ensure cleanup continues even if errors occur
            self.container = None
            self.cli_app = None

    def _load_configuration(self) -> None:
        """Load application configuration."""
        try:
            config_manager = ConfigurationManager()
            self.config = config_manager.load_config()
        except Exception as e:
            raise ApplicationError(f"Failed to load configuration: {e}") from e

    def _configure_logging(self) -> None:
        """Configure logging based on application configuration."""
        try:
            log_level = self._get_logging_level(self.config.environment)
            log_format = self.config.log_format

            logging.basicConfig(
                level=log_level,
                format=log_format,
                force=True,  # Override any existing configuration
            )

        except Exception as e:
            raise ApplicationError(f"Failed to configure logging: {e}") from e

    def _create_container(self) -> None:
        """Create the dependency injection container."""
        self.container = ServiceContainer()

    def _configure_services(self) -> None:
        """Configure all services in the dependency injection container."""
        try:
            configurator = ServiceConfigurator(self.container, self.config)
            configurator.configure_all()
        except Exception as e:
            raise ApplicationError(f"Failed to configure services: {e}") from e

    def _create_cli_app(self) -> None:
        """Create the CLI application."""
        self.cli_app = CLIApp()

        # Register CLI commands here
        # This will be expanded when CLI commands are integrated

    def _get_logging_level(self, environment: Environment) -> int:
        """Get the appropriate logging level for the environment.

        Args:
            environment: The application environment

        Returns:
            The logging level constant

        """
        if environment == Environment.DEVELOPMENT:
            return logging.DEBUG
        elif environment == Environment.TEST:
            return logging.WARNING
        elif environment == Environment.PRODUCTION:
            return logging.INFO
        else:
            return logging.INFO  # Default to INFO
