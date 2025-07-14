from rich.console import Console
from rich.table import Table


class CLIApp:
    """A simple command-line interface application."""

    def __init__(self):
        self.console = Console()
        self.commands = {}

    def register_command(self, name, handler):
        """Register a command with the CLI application."""
        self.commands[name] = handler

    def run(self, args):
        """Run the CLI application, executing the specified command."""
        if not args:
            self.show_help()
            return

        command_name = args[0]
        if command_name in self.commands:
            self.commands[command_name](args[1:])
        else:
            self.console.print(f"[red]Error: Unknown command '{command_name}'[/red]")
            self.show_help()

    def show_help(self):
        """Display the help message and list available commands."""
        self.console.print("[bold green]Meeting Room Reservation System CLI[/bold green]")
        self.console.print("\n[bold]Available Commands:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command")
        table.add_column("Description")

        if not self.commands:
            table.add_row("[italic]No commands registered.[/italic]", "")
        else:
            for name, handler in self.commands.items():
                table.add_row(name, handler.__doc__ or "No description provided.")
        self.console.print(table)
