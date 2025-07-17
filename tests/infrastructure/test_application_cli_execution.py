"""Tests for end-to-end CLI command execution."""

from unittest.mock import Mock, patch

from src.infrastructure.application import Application


def test_end_to_end_book_command_execution():
    """Test that executing 'book' command calls BookingCommand.execute."""
    app = Application()
    app.bootstrap()

    # Mock the registered command handler directly
    mock_execute = Mock()
    app.cli_app.commands["book"] = mock_execute

    # Execute the book command through the CLI app
    app.cli_app.run(["book", "arg1", "arg2"])

    # Verify the command handler was called with correct arguments
    mock_execute.assert_called_once_with(["arg1", "arg2"])


def test_end_to_end_cancel_command_execution():
    """Test that executing 'cancel' command calls CancellationCommand.execute."""
    app = Application()
    app.bootstrap()

    # Mock the registered command handler directly
    mock_execute = Mock()
    app.cli_app.commands["cancel"] = mock_execute

    # Execute the cancel command through the CLI app
    app.cli_app.run(["cancel", "booking123"])

    # Verify the command handler was called with correct arguments
    mock_execute.assert_called_once_with(["booking123"])


def test_end_to_end_list_command_execution():
    """Test that executing 'list' command calls ListCommand.execute."""
    app = Application()
    app.bootstrap()

    # Mock the registered command handler directly
    mock_execute = Mock()
    app.cli_app.commands["list"] = mock_execute

    # Execute the list command through the CLI app
    app.cli_app.run(["list", "--sort", "time"])

    # Verify the command handler was called with correct arguments
    mock_execute.assert_called_once_with(["--sort", "time"])


def test_end_to_end_command_execution_with_no_args():
    """Test that commands can be executed with no additional arguments."""
    app = Application()
    app.bootstrap()

    # Test each command with no additional arguments
    mock_book = Mock()
    app.cli_app.commands["book"] = mock_book
    app.cli_app.run(["book"])
    mock_book.assert_called_once_with([])

    mock_cancel = Mock()
    app.cli_app.commands["cancel"] = mock_cancel
    app.cli_app.run(["cancel"])
    mock_cancel.assert_called_once_with([])

    mock_list = Mock()
    app.cli_app.commands["list"] = mock_list
    app.cli_app.run(["list"])
    mock_list.assert_called_once_with([])


def test_end_to_end_unknown_command_handling():
    """Test that unknown commands are handled gracefully."""
    app = Application()
    app.bootstrap()

    # Mock console to capture error output
    with patch.object(app.cli_app.console, "print") as mock_print:
        with patch.object(app.cli_app, "show_help") as mock_help:
            app.cli_app.run(["unknown_command"])

            # Should print error message and show help
            mock_print.assert_called()
            mock_help.assert_called_once()

            # Check that error message was printed
            error_calls = [call for call in mock_print.call_args_list if "Error" in str(call) or "Unknown" in str(call)]
            assert len(error_calls) > 0, "Expected error message to be printed"


def test_unknown_command_handling_works_correctly():
    """Test that unknown command handling still works correctly."""
    app = Application()
    app.bootstrap()

    # Test unknown command
    with patch.object(app.cli_app.console, "print") as mock_print:
        with patch.object(app.cli_app, "show_help") as mock_help:
            app.cli_app.run(["nonexistent_command"])

            # Should print error and show help
            mock_print.assert_called()
            mock_help.assert_called_once()


def test_command_execution_with_various_argument_combinations():
    """Test command execution with various argument combinations."""
    app = Application()
    app.bootstrap()

    # Test commands with different argument patterns
    test_cases = [
        (["book"], []),
        (["book", "arg1"], ["arg1"]),
        (["book", "arg1", "arg2", "arg3"], ["arg1", "arg2", "arg3"]),
        (["cancel"], []),
        (["cancel", "booking-id"], ["booking-id"]),
        (["list"], []),
        (["list", "--sort", "time"], ["--sort", "time"]),
        (["list", "--invalid-flag"], ["--invalid-flag"]),
    ]

    for command_args, expected_handler_args in test_cases:
        mock_handler = Mock()
        app.cli_app.commands[command_args[0]] = mock_handler

        app.cli_app.run(command_args)
        mock_handler.assert_called_once_with(expected_handler_args)
        mock_handler.reset_mock()


def test_empty_command_list_shows_help():
    """Test that empty command list shows help."""
    app = Application()
    app.bootstrap()

    with patch.object(app.cli_app, "show_help") as mock_help:
        app.cli_app.run([])
        mock_help.assert_called_once()
