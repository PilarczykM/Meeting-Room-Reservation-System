"""Tests for enhanced signal handling in main entry point."""

import signal
from unittest.mock import Mock, patch

from main import ApplicationRunner, setup_signal_handlers


class TestEnhancedSignalHandling:
    """Test cases for enhanced signal handling."""

    def test_signal_handler_calls_runner_shutdown(self):
        """Test that signal handler calls runner.shutdown()."""
        runner = Mock()

        with patch("main.logger"):
            # Set up signal handlers
            setup_signal_handlers(runner)

            # Get the signal handler function
            signal_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal_handler)

            # Simulate receiving SIGINT
            with patch("sys.exit"):
                try:
                    # Call the signal handler directly
                    signal_handler = signal.getsignal(signal.SIGINT)
                    if callable(signal_handler):
                        signal_handler(signal.SIGINT, None)
                except SystemExit:
                    pass

                # Verify shutdown was called
                runner.shutdown.assert_called_once()

    def test_signal_handler_exits_with_130_for_sigint(self):
        """Test that signal handler exits with code 130 for SIGINT."""
        runner = Mock()

        with patch("main.logger"):
            setup_signal_handlers(runner)

            # Get the actual signal handler
            signal_handler = signal.getsignal(signal.SIGINT)

            with patch("sys.exit") as mock_exit:
                if callable(signal_handler):
                    signal_handler(signal.SIGINT, None)
                    mock_exit.assert_called_with(130)

    def test_signal_handler_exits_with_1_for_sigterm(self):
        """Test that signal handler exits with code 1 for SIGTERM."""
        runner = Mock()

        with patch("main.logger"):
            setup_signal_handlers(runner)

            # Get the actual signal handler
            signal_handler = signal.getsignal(signal.SIGTERM)

            with patch("sys.exit") as mock_exit:
                if callable(signal_handler):
                    signal_handler(signal.SIGTERM, None)
                    mock_exit.assert_called_with(1)

    def test_signal_handler_logs_shutdown_message(self):
        """Test that signal handler logs appropriate shutdown message."""
        runner = Mock()

        with patch("main.logger") as mock_logger:
            setup_signal_handlers(runner)

            signal_handler = signal.getsignal(signal.SIGINT)

            with patch("sys.exit"):
                if callable(signal_handler):
                    signal_handler(signal.SIGINT, None)

                    # Verify logging was called with SIGINT message
                    mock_logger.info.assert_called_with("Received SIGINT, initiating graceful shutdown...")

    def test_signal_handler_handles_shutdown_exceptions(self):
        """Test that signal handler handles exceptions during shutdown gracefully."""
        runner = Mock()
        runner.shutdown.side_effect = Exception("Shutdown failed")

        with patch("main.logger"):
            setup_signal_handlers(runner)

            signal_handler = signal.getsignal(signal.SIGINT)

            with patch("sys.exit") as mock_exit:
                if callable(signal_handler):
                    signal_handler(signal.SIGINT, None)

                    # Should still exit even if shutdown fails
                    mock_exit.assert_called_with(130)

    def test_application_runner_handles_keyboard_interrupt(self):
        """Test that ApplicationRunner properly handles KeyboardInterrupt."""
        # This test verifies that KeyboardInterrupt returns exit code 130
        # We'll test this through direct exception raising
        args = Mock()
        runner = ApplicationRunner(args)

        # Directly test the exception handling logic
        with patch.object(runner, "_configure_logging", side_effect=KeyboardInterrupt()):
            exit_code = runner.run()
            assert exit_code == 130

    def test_application_runner_cleanup_called_on_keyboard_interrupt(self):
        """Test that cleanup is called even when KeyboardInterrupt occurs."""
        args = Mock()
        args.verbose = False
        args.quiet = False
        args.command = None
        args.args = []
        args.environment = None
        args.config_file = None

        runner = ApplicationRunner(args)

        with (
            patch.object(runner, "_configure_logging"),
            patch.object(runner, "_load_configuration"),
            patch.object(runner, "_cleanup") as mock_cleanup,
            patch("src.infrastructure.application.Application") as mock_app_class,
        ):
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = KeyboardInterrupt()

            runner.run()

            # Verify cleanup was called
            mock_cleanup.assert_called_once()
