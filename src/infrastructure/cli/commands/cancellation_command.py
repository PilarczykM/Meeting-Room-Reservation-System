from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.application.commands.commands import CancelBookingCommand
from src.application.dtos.cancellation_request import CancellationRequest
from src.application.exceptions import CancellationFailedError


class CancellationCommand:
    """Interactive command for canceling a meeting room booking."""

    def __init__(self, cancellation_service, query_service):
        """Initialize the cancellation command with required services."""
        self.cancellation_service = cancellation_service
        self.query_service = query_service
        self.console = Console()

    def execute(self, args):
        """Execute the cancellation command with interactive prompts."""
        self.console.print(Panel.fit("[bold red]Cancel Meeting Room Booking[/bold red]", border_style="red"))

        try:
            # Get booking ID from user
            booking_id = self._get_booking_id_input()
            if not booking_id:
                self.console.print("[yellow]Cancellation cancelled.[/yellow]")
                return

            # Find and display the booking
            booking = self._find_booking(booking_id)
            if not booking:
                self.console.print(f"[red]Booking with ID '{booking_id}' not found.[/red]")
                return

            # Show booking details and confirm cancellation
            if not self._confirm_cancellation(booking):
                self.console.print("[yellow]Cancellation cancelled.[/yellow]")
                return

            # Cancel the booking
            self._cancel_booking(booking_id)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Cancellation cancelled.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")

    def _get_booking_id_input(self):
        """Get booking ID from user input."""
        while True:
            booking_id = input("Enter booking ID to cancel (or press Enter to exit): ").strip()
            if not booking_id:
                return None

            # Basic validation - booking ID should not be empty
            if booking_id:
                return booking_id
            else:
                self.console.print("[red]Booking ID cannot be empty. Please try again.[/red]")

    def _find_booking(self, booking_id):
        """Find a booking by its ID."""
        try:
            all_bookings = self.query_service.get_all_bookings()
            for booking in all_bookings:
                if booking["booking_id"] == booking_id:
                    return booking
            else:
                return None
        except Exception as e:
            self.console.print(f"[red]Error retrieving bookings: {e}[/red]")
            return None

    def _confirm_cancellation(self, booking):
        """Show booking details and ask for cancellation confirmation."""
        self.console.print("\n[bold]Booking to Cancel:[/bold]")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        # Parse datetime strings for display
        try:
            start_time = datetime.fromisoformat(booking["start_time"])
            end_time = datetime.fromisoformat(booking["end_time"])

            table.add_row("Booking ID:", booking["booking_id"])
            table.add_row("Start Time:", start_time.strftime("%Y-%m-%d %H:%M"))
            table.add_row("End Time:", end_time.strftime("%Y-%m-%d %H:%M"))
            table.add_row("Booker:", booking["booker"])
            table.add_row("Attendees:", str(booking["attendees"]))
        except (ValueError, KeyError) as e:
            self.console.print(f"[red]Error displaying booking details: {e}[/red]")
            return False

        self.console.print(table)

        while True:
            confirm = (
                input("\n[bold red]Are you sure you want to cancel this booking? (y/n): [/bold red]").strip().lower()
            )
            if confirm in ["y", "yes"]:
                return True
            elif confirm in ["n", "no"]:
                return False
            else:
                self.console.print("[red]Please enter 'y' for yes or 'n' for no.[/red]")

    def _cancel_booking(self, booking_id):
        """Cancel the booking using the cancellation service."""
        try:
            # Create cancellation request
            cancellation_request = CancellationRequest(booking_id=booking_id)

            # Create command and execute
            command = CancelBookingCommand(request=cancellation_request)
            self.cancellation_service.cancel_booking(command)

            # Show success message
            self.console.print(
                Panel.fit(
                    f"[bold green]Booking Cancelled Successfully![/bold green]\n"
                    f"Booking ID: [cyan]{booking_id}[/cyan] has been cancelled.",
                    border_style="green",
                )
            )

        except CancellationFailedError as e:
            self.console.print(
                Panel.fit(f"[bold red]Cancellation Failed![/bold red]\nError: {e!s}", border_style="red")
            )
        except Exception as e:
            self.console.print(
                Panel.fit(
                    f"[bold red]Cancellation Failed![/bold red]\nAn unexpected error occurred: {e!s}",
                    border_style="red",
                )
            )
