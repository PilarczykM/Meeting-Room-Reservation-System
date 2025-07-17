"""Tests for the main application entry point."""

import logging
import signal
import sys
from argparse import Namespace
from unittest.mock import Mock, patch

import pytest

from main import ApplicationRunner, main, parse_arguments, setup_signal_handlers


class TestMainEntryPoint:
    """Test cases for main application entry point."""

    def test_parse_arguments_no_args(self):
        """Test parsing arguments with no command provided."""
        args = parse_arguments([])

        assert args.command is None
        assert args.verbose is False
        assert args.quiet is False
        assert args.config_file is None
        assert args.environment is None

    def test_parse_arguments_with_command(self):
        """Test parsing arguments with a command."""
        args = parse_arguments(["book", "--room", "A", "--time", "10:00"])

        assert args.command == "book"
        assert "--room" in args.args
        assert "A" in args.args
        assert "--time" in args.args
        assert "10:00" in args.args

    def test_parse_arguments_with_verbose_flag(self):
        """Test parsing arguments with verbose flag."""
        args = parse_arguments(["--verbose", "list"])

        assert args.verbose is True
        assert args.command == "list"

    def test_parse_arguments_with_quiet_flag(self):
        """Test parsing arguments with quiet flag."""
        args = parse_arguments(["--quiet", "cancel", "123"])

        assert args.quiet is True
        assert args.command == "cancel"
        assert "123" in args.args

    def test_parse_arguments_with_config_file(self):
        """Test parsing arguments with custom config file."""
        args = parse_arguments(["--config", "/path/to/config.json", "book"])

        assert args.config_file == "/path/to/config.json"
        assert args.command == "book"

    def test_parse_arguments_with_environment(self):
        """Test parsing arguments with environment override."""
        args = parse_arguments(["--env", "production", "list"])

        assert args.environment == "production"
        assert args.command == "list"

    def test_parse_arguments_help_flag(self):
        """Test that help flag works correctly."""
        with pytest.raises(SystemExit):
            parse_arguments(["--help"])

    def test_application_runner_initialization(self):
        """Test ApplicationRunner initialization."""
        args = Namespace(verbose=False, quiet=False, config_file=None, environment=None)
        runner = ApplicationRunner(args)

        assert runner.args is args
        assert runner.app is None

    def test_application_runner_run_success(self):
        """Test successful application run."""
        args = Namespace(verbose=False, quiet=False, config_file=None, environment=None, command="list", args=[])
        runner = ApplicationRunner(args)

        with patch("main.Application") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            exit_code = runner.run()

            # Should bootstrap and run the application
            mock_app.bootstrap.assert_called_once()
            mock_app.run.assert_called_once_with(["list"])
            assert exit_code == 0

    def test_application_runner_run_with_no_command(self):
        """Test application run with no command shows help."""
        args = Namespace(verbose=False, quiet=False, config_file=None, environment=None, command=None, args=[])
        runner = ApplicationRunner(args)

        with patch("main.Application") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            exit_code = runner.run()

            # Should bootstrap and run with empty args (shows help)
            mock_app.bootstrap.assert_called_once()
            mock_app.run.assert_called_once_with([])
            assert exit_code == 0

    def test_application_runner_handles_application_error(self):
        """Test that ApplicationRunner handles application errors gracefully."""
        args = Namespace(
            verbose=False, quiet=False, config_file=None, environment=None, command="book", args=["--room", "A"]
        )
        runner = ApplicationRunner(args)

        with patch("main.Application") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.bootstrap.side_effect = Exception("Bootstrap failed")

            with patch("main.logger") as mock_logger:
                exit_code = runner.run()

                # Should log error and return error code
                mock_logger.exception.assert_called()
                assert exit_code == 1

    def test_application_runner_handles_keyboard_interrupt(self):
        """Test that ApplicationRunner handles KeyboardInterrupt gracefully."""
        args = Namespace(
            verbose=False, quiet=False, config_file=None, environment=None, command="book", args=["--room", "A"]
        )
        runner = ApplicationRunner(args)

        with patch("main.Application") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = KeyboardInterrupt()

            with patch("main.logger") as mock_logger:
                exit_code = runner.run()

                # Should log interruption and return error code
                mock_logger.info.assert_called_with("Application interrupted by user")
                assert exit_code == 130  # Standard exit code for SIGINT

    def test_application_runner_cleanup_on_exit(self):
        """Test that ApplicationRunner cleans up resources on exit."""
        args = Namespace(verbose=False, quiet=False, config_file=None, environment=None, command="list", args=[])
        runner = ApplicationRunner(args)

        with patch("main.Application") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            runner.run()

            # Should call shutdown
            mock_app.shutdown.assert_called_once()

    def test_application_runner_cleanup_on_error(self):
        """Test that ApplicationRunner cleans up resources even on error."""
        args = Namespace(
            verbose=False, quiet=False, config_file=None, environment=None, command="book", args=["--room", "A"]
        )
        runner = ApplicationRunner(args)

        with patch("main.Application") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = Exception("Runtime error")

            with patch("main.logger"):
                runner.run()

                # Should still call shutdown
                mock_app.shutdown.assert_called_once()

    def test_setup_signal_handlers(self):
        """Test that signal handlers are set up correctly."""
        runner = Mock()

        with patch("signal.signal") as mock_signal:
            setup_signal_handlers(runner)

            # Should set up SIGINT and SIGTERM handlers
            assert mock_signal.call_count == 2
            calls = mock_signal.call_args_list

            # Check SIGINT handler
            sigint_call = next(call for call in calls if call[0][0] == signal.SIGINT)
            assert sigint_call is not None

            # Check SIGTERM handler
            sigterm_call = next(call for call in calls if call[0][0] == signal.SIGTERM)
            assert sigterm_call is not None

    def test_signal_handler_calls_shutdown(self):
        """Test that signal handler calls shutdown on the runner."""
        runner = Mock()

        with patch("signal.signal") as mock_signal:
            with patch("sys.exit") as mock_exit:  # Mock sys.exit to prevent test termination
                setup_signal_handlers(runner)

                # Find the SIGINT handler from the mock calls
                sigint_handler = None
                for call in mock_signal.call_args_list:
                    if call[0][0] == signal.SIGINT:
                        sigint_handler = call[0][1]
                        break

                assert sigint_handler is not None, "SIGINT handler should be registered"

                # Call the handler
                sigint_handler(signal.SIGINT, None)

                # Should call shutdown on runner
                runner.shutdown.assert_called_once()
                # Should also call sys.exit
                mock_exit.assert_called_once_with(130)

    def test_main_function_success(self):
        """Test main function with successful execution."""
        test_args = ["main.py", "list"]

        with patch.object(sys, "argv", test_args):
            with patch("main.ApplicationRunner") as mock_runner_class:
                mock_runner = Mock()
                mock_runner.run.return_value = 0
                mock_runner_class.return_value = mock_runner

                with patch("main.setup_signal_handlers") as mock_setup_signals:
                    exit_code = main()

                    # Should create runner and set up signals
                    mock_runner_class.assert_called_once()
                    mock_setup_signals.assert_called_once_with(mock_runner)
                    mock_runner.run.assert_called_once()
                    assert exit_code == 0

    def test_main_function_with_error(self):
        """Test main function with error during execution."""
        test_args = ["main.py", "book", "--room", "A"]

        with patch.object(sys, "argv", test_args):
            with patch("main.ApplicationRunner") as mock_runner_class:
                mock_runner = Mock()
                mock_runner.run.return_value = 1
                mock_runner_class.return_value = mock_runner

                with patch("main.setup_signal_handlers"):
                    exit_code = main()

                    assert exit_code == 1

    def test_main_function_handles_unexpected_error(self):
        """Test main function handles unexpected errors gracefully."""
        test_args = ["main.py", "list"]

        with patch.object(sys, "argv", test_args):
            with patch("main.ApplicationRunner") as mock_runner_class:
                mock_runner_class.side_effect = Exception("Unexpected error")

                with patch("main.logger") as mock_logger:
                    exit_code = main()

                    # Should log error and return error code
                    mock_logger.exception.assert_called()
                    assert exit_code == 1

    def test_verbose_logging_configuration(self):
        """Test that verbose flag configures logging appropriately."""
        args = Namespace(verbose=True, quiet=False, config_file=None, environment=None)
        runner = ApplicationRunner(args)

        with patch("logging.basicConfig") as mock_basic_config:
            runner._configure_logging()

            # Should configure verbose logging
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs.get("level") == logging.DEBUG

    def test_quiet_logging_configuration(self):
        """Test that quiet flag configures logging appropriately."""
        args = Namespace(verbose=False, quiet=True, config_file=None, environment=None)
        runner = ApplicationRunner(args)

        with patch("logging.basicConfig") as mock_basic_config:
            runner._configure_logging()

            # Should configure quiet logging
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs.get("level") == logging.WARNING

    def test_config_file_loading(self):
        """Test that custom config file is loaded correctly."""
        args = Namespace(verbose=False, quiet=False, config_file="/custom/config.json", environment=None)
        runner = ApplicationRunner(args)

        with patch("main.ConfigurationManager") as mock_config_manager:
            with patch("main.Application"):
                mock_config = Mock()
                mock_config_manager.return_value.load_config.return_value = mock_config

                runner.run()

                # Should load config from custom file
                mock_config_manager.assert_called_once()

    def test_environment_override(self):
        """Test that environment can be overridden via command line."""
        args = Namespace(verbose=False, quiet=False, config_file=None, environment="production")
        runner = ApplicationRunner(args)

        with patch("main.ConfigurationManager") as mock_config_manager:
            with patch("main.Application"):
                runner.run()

                # Should load config with environment override
                mock_config_manager.return_value.load_config.assert_called_with(env="production")
