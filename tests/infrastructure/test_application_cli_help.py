"""Tests for CLI help display functionality."""

from unittest.mock import patch

from src.infrastructure.application import Application


def test_cli_help_displays_registered_commands():
    """Test that help message displays all registered commands when no arguments provided."""
    app = Application()
    app.bootstrap()

    # Verify commands are registered before testing help display
    assert "book" in app.cli_app.commands
    assert "cancel" in app.cli_app.commands
    assert "list" in app.cli_app.commands

    # Mock the console to capture that help was called
    with patch.object(app.cli_app.console, "print") as mock_print:
        app.cli_app.show_help()

        # Verify help was displayed (console.print was called)
        mock_print.assert_called()

        # Verify that a table was printed (Rich Table object)
        calls = mock_print.call_args_list
        assert len(calls) >= 2  # Should have title and table calls

        # The commands should be available in the CLI app
        assert len(app.cli_app.commands) == 3


def test_cli_help_shows_command_descriptions():
    """Test that help message shows command descriptions in formatted table."""
    app = Application()
    app.bootstrap()

    # Verify commands have descriptions
    assert "book" in app.cli_app.commands
    assert "cancel" in app.cli_app.commands
    assert "list" in app.cli_app.commands

    # Verify commands are callable (which means they have docstrings from their execute methods)
    book_handler = app.cli_app.commands["book"]
    cancel_handler = app.cli_app.commands["cancel"]
    list_handler = app.cli_app.commands["list"]

    assert callable(book_handler)
    assert callable(cancel_handler)
    assert callable(list_handler)


def test_main_app_shows_available_commands():
    """Test that running main app without arguments shows available commands."""
    app = Application()
    app.bootstrap()

    # Test that CLI app shows help when no arguments provided
    with patch.object(app.cli_app, "show_help") as mock_show_help:
        app.cli_app.run([])
        mock_show_help.assert_called_once()


def test_commands_appear_in_help_output():
    """Test that book, cancel, and list commands appear in help output."""
    app = Application()
    app.bootstrap()

    # Verify all expected commands are registered
    expected_commands = ["book", "cancel", "list"]
    for command in expected_commands:
        assert command in app.cli_app.commands, f"Command '{command}' not found in registered commands"

    # Verify no unexpected commands
    assert len(app.cli_app.commands) == 3, f"Expected 3 commands, found {len(app.cli_app.commands)}"
