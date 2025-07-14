from unittest.mock import MagicMock

import pytest

from src.infrastructure.cli.app import CLIApp


@pytest.fixture
def cli_app(mocker):
    mocker.patch("src.infrastructure.cli.app.Console", autospec=True)
    return CLIApp()


def test_cli_app_initialization(cli_app):
    assert cli_app.console is not None
    assert cli_app.commands == {}


def test_register_command(cli_app):
    def mock_command():
        pass

    cli_app.register_command("test", mock_command)
    assert "test" in cli_app.commands
    assert cli_app.commands["test"] == mock_command


def test_run_existing_command(cli_app):
    mock_handler = MagicMock()
    cli_app.register_command("test", mock_handler)
    cli_app.run(["test", "arg1", "arg2"])
    mock_handler.assert_called_once_with(["arg1", "arg2"])


def test_run_unknown_command(cli_app):
    cli_app.run(["unknown_command"])
    cli_app.console.print.assert_any_call("[red]Error: Unknown command 'unknown_command'[/red]")
    cli_app.console.print.assert_any_call("[bold green]Meeting Room Reservation System CLI[/bold green]")


def test_run_no_args_shows_help(cli_app):
    cli_app.run([])
    cli_app.console.print.assert_any_call("[bold green]Meeting Room Reservation System CLI[/bold green]")


def test_show_help_no_commands(cli_app, mocker):
    # Mock the Table class to capture what's added to it
    mock_table = mocker.patch("src.infrastructure.cli.app.Table")
    table_instance = mock_table.return_value

    cli_app.show_help()

    # Check that add_row was called with the "No commands registered" message
    table_instance.add_row.assert_called_with("[italic]No commands registered.[/italic]", "")


def test_show_help_with_commands(cli_app, mocker):
    # Mock the Table class to capture what's added to it
    mock_table_class = mocker.patch("src.infrastructure.cli.app.Table")
    mock_table_instance = mock_table_class.return_value

    def command_with_doc():
        """This is a test command."""
        pass

    def command_without_doc():
        pass

    cli_app.register_command("cmd1", command_with_doc)
    cli_app.register_command("cmd2", command_without_doc)
    cli_app.show_help()

    # Verify the table was created with correct parameters
    mock_table_class.assert_called_once_with(show_header=True, header_style="bold magenta")

    # Verify the correct columns were added
    mock_table_instance.add_column.assert_any_call("Command")
    mock_table_instance.add_column.assert_any_call("Description")

    # Verify the correct rows were added
    mock_table_instance.add_row.assert_any_call("cmd1", "This is a test command.")
    mock_table_instance.add_row.assert_any_call("cmd2", "No description provided.")

    # Verify the table was printed
    cli_app.console.print.assert_called_with(mock_table_instance)
