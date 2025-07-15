#!/usr/bin/env python3
"""Main application entry point for the Meeting Room Reservation System."""

import argparse
import logging
import signal
import sys

from src.infrastructure.application import Application, ApplicationError
from src.infrastructure.config.manager import ConfigurationManager
from src.infrastructure.config.models import ApplicationConfig

# Set up logging for the main module
logger = logging.getLogger(__name__)


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of arguments to parse. If None, uses sys.argv

    Returns:
        Parsed arguments namespace

    """
    parser = argparse.ArgumentParser(description="Meeting Room Reservation System", prog="meeting-room-system")

    # Global options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    parser.add_argument("--quiet", "-q", action="store_true", help="Enable quiet mode (minimal logging)")

    parser.add_argument("--config", "-c", dest="config_file", help="Path to configuration file")

    parser.add_argument(
        "--env",
        "-e",
        dest="environment",
        choices=["development", "test", "production"],
        help="Override environment setting",
    )

    # Command and remaining arguments
    parser.add_argument("command", nargs="?", help="Command to execute (book, cancel, list)")

    # Use REMAINDER to capture all remaining arguments as-is
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments for the command")

    return parser.parse_args(args)


class ApplicationRunner:
    """Handles application execution with proper error handling and cleanup."""

    def __init__(self, args: argparse.Namespace):
        """Initialize the application runner.

        Args:
            args: Parsed command-line arguments

        """
        self.args = args
        self.app: Application | None = None
        self._shutdown_requested = False

    def run(self) -> int:
        """Run the application.

        Returns:
            Exit code (0 for success, non-zero for error)

        """
        try:
            # Configure logging based on command-line flags
            self._configure_logging()

            # Load configuration
            config = self._load_configuration()

            # Create and bootstrap application
            self.app = Application(config=config)
            self.app.bootstrap()

            # Prepare command arguments
            command_args = []
            if self.args.command:
                command_args = [self.args.command, *self.args.args]

            # Run the application
            self.app.run(command_args)
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            return 130  # Standard exit code for SIGINT
        except ApplicationError as e:
            logger.exception("Application error")
            if hasattr(e, "details") and e.details:
                logger.debug(f"Error details: {e.details}")
            return 1
        except Exception:
            logger.exception("Unexpected error")
            return 1
        else:
            return 0
        finally:
            # Always clean up resources
            self._cleanup()

    def shutdown(self) -> None:
        """Request graceful shutdown of the application."""
        self._shutdown_requested = True
        logger.info("Shutdown requested")

        if self.app:
            try:
                self.app.shutdown()
            except Exception:
                logger.exception("Error during shutdown")

    def _configure_logging(self) -> None:
        """Configure logging based on command-line arguments."""
        if self.args.verbose:
            level = logging.DEBUG
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        elif self.args.quiet:
            level = logging.WARNING
            format_str = "%(levelname)s - %(message)s"
        else:
            level = logging.INFO
            format_str = "%(asctime)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=level,
            format=format_str,
            force=True,  # Override any existing configuration
        )

    def _load_configuration(self) -> ApplicationConfig:
        """Load application configuration.

        Returns:
            Loaded and validated configuration

        Raises:
            ApplicationError: If configuration loading fails

        """
        try:
            config_manager = ConfigurationManager()

            # Load configuration with optional environment override
            config = config_manager.load_config(env=self.args.environment)

            # TODO: Handle custom config file if provided
            if self.args.config_file:
                logger.info(f"Custom config file specified: {self.args.config_file}")
                # This would require extending ConfigurationManager to support custom files
        except Exception as e:
            raise ApplicationError(f"Failed to load configuration: {e}") from e
        else:
            return config

    def _cleanup(self) -> None:
        """Clean up application resources."""
        if self.app:
            try:
                self.app.shutdown()
            except Exception:
                logger.exception("Error during cleanup")
            finally:
                self.app = None


def setup_signal_handlers(runner: ApplicationRunner) -> None:
    """Set up signal handlers for graceful shutdown.

    Args:
        runner: Application runner instance to shutdown on signal

    """

    def signal_handler(signum: int, frame) -> None:
        """Handle shutdown signals."""
        signal_names = {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM"}
        signal_name = signal_names.get(signum, f"Signal {signum}")
        logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        runner.shutdown()

    # Set up handlers for common shutdown signals
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination request


def main() -> int:
    """Run the main application entry point.

    Returns:
        Exit code (0 for success, non-zero for error)

    """
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Create application runner
        runner = ApplicationRunner(args)

        # Set up signal handlers for graceful shutdown
        setup_signal_handlers(runner)

        # Run the application
        return runner.run()

    except Exception:
        # Handle any unexpected errors in main
        logger.exception("Fatal error in main")
        return 1


if __name__ == "__main__":
    sys.exit(main())
