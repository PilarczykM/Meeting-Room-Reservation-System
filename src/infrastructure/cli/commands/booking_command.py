from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.application.commands.commands import CreateBookingCommand
from src.application.dtos.booking_request import BookingRequest
from src.domain.exceptions import InvalidAttendeeCountError, OverlappingBookingError


class BookingCommand:
    """Interactive command for booking a meeting room."""

    def __init__(self, booking_service):
        """Initialize the booking command with required services."""
        self.booking_service = booking_service
        self.console = Console()

    def execute(self, args):
        """Execute the booking command with interactive prompts."""
        self.console.print(Panel.fit("[bold green]Meeting Room Booking[/bold green]", border_style="green"))

        try:
            # Collect booking information interactively
            booking_data = self._collect_booking_information()
            if not booking_data:
                self.console.print("[yellow]Booking cancelled.[/yellow]")
                return

            # Show confirmation
            if not self._confirm_booking(booking_data):
                self.console.print("[yellow]Booking cancelled.[/yellow]")
                return

            # Create the booking
            self._create_booking(booking_data)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Booking cancelled.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")

    def _collect_booking_information(self):
        """Collect booking information from user input."""
        booking_data = {}

        # Get start time
        booking_data["start_time"] = self._get_datetime_input("Enter start time (YYYY-MM-DD HH:MM): ")
        if not booking_data["start_time"]:
            return None

        # Get end time
        while True:
            booking_data["end_time"] = self._get_datetime_input("Enter end time (YYYY-MM-DD HH:MM): ")
            if not booking_data["end_time"]:
                return None

            if booking_data["end_time"] <= booking_data["start_time"]:
                self.console.print("[red]End time must be after start time. Please try again.[/red]")
                continue
            break

        # Get booker name
        while True:
            booker = input("Enter your name: ").strip()
            if booker:
                booking_data["booker"] = booker
                break
            self.console.print("[red]Name cannot be empty. Please try again.[/red]")

        # Get attendees count
        booking_data["attendees"] = self._get_attendees_input()
        if not booking_data["attendees"]:
            return None

        return booking_data

    def _get_datetime_input(self, prompt):
        """Get and validate datetime input from user."""
        while True:
            try:
                time_str = input(prompt).strip()
                if not time_str:
                    return None

                # Parse the datetime
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")

                # Check if the time is in the past
                if dt <= datetime.now():
                    self.console.print("[red]Cannot book in the past. Please enter a future time.[/red]")
                    continue
                else:
                    return dt

            except ValueError:
                self.console.print("[red]Invalid date format. Please use YYYY-MM-DD HH:MM format.[/red]")
                continue

    def _get_attendees_input(self):
        """Get and validate attendees count from user."""
        while True:
            try:
                attendees_str = input("Enter number of attendees (4-20): ").strip()
                if not attendees_str:
                    return None

                attendees = int(attendees_str)

                if attendees < 4:
                    self.console.print("[red]Minimum 4 attendees required. Please try again.[/red]")
                    continue
                elif attendees > 20:
                    self.console.print("[red]Maximum 20 attendees allowed. Please try again.[/red]")
                    continue
                else:
                    return attendees

            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")
                continue

    def _confirm_booking(self, booking_data):
        """Show booking details and ask for confirmation."""
        self.console.print("\n[bold]Booking Summary:[/bold]")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Start Time:", booking_data["start_time"].strftime("%Y-%m-%d %H:%M"))
        table.add_row("End Time:", booking_data["end_time"].strftime("%Y-%m-%d %H:%M"))
        table.add_row("Booker:", booking_data["booker"])
        table.add_row("Attendees:", str(booking_data["attendees"]))

        self.console.print(table)

        while True:
            confirm = input("\nConfirm booking? (y/n): ").strip().lower()
            if confirm in ["y", "yes"]:
                return True
            elif confirm in ["n", "no"]:
                return False
            else:
                self.console.print("[red]Please enter 'y' for yes or 'n' for no.[/red]")

    def _create_booking(self, booking_data):
        """Create the booking using the booking service."""
        try:
            # Create booking request
            booking_request = BookingRequest(
                start_time=booking_data["start_time"],
                end_time=booking_data["end_time"],
                booker=booking_data["booker"],
                attendees=booking_data["attendees"],
            )

            # Create command and execute
            command = CreateBookingCommand(request=booking_request)
            response = self.booking_service.create_booking(command)

            # Show success message
            self.console.print(
                Panel.fit(
                    f"[bold green]Booking Created Successfully![/bold green]\n"
                    f"Booking ID: [cyan]{response.booking_id}[/cyan]\n"
                    f"Time: {response.start_time.strftime('%Y-%m-%d %H:%M')} - "
                    f"{response.end_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Booker: {response.booker}\n"
                    f"Attendees: {response.attendees}",
                    border_style="green",
                )
            )

        except OverlappingBookingError as e:
            self.console.print(
                Panel.fit(
                    f"[bold red]Booking Failed![/bold red]\n"
                    f"The requested time slot conflicts with an existing booking.\n"
                    f"Error: {e!s}",
                    border_style="red",
                )
            )
        except InvalidAttendeeCountError as e:
            self.console.print(
                Panel.fit(
                    f"[bold red]Booking Failed![/bold red]\nInvalid number of attendees.\nError: {e!s}",
                    border_style="red",
                )
            )
        except Exception as e:
            self.console.print(
                Panel.fit(
                    f"[bold red]Booking Failed![/bold red]\nAn unexpected error occurred: {e!s}", border_style="red"
                )
            )
