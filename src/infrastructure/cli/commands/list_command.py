from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class ListCommand:
    """Interactive command for listing all meeting room bookings."""

    def __init__(self, query_service):
        """Initialize the list command with required services."""
        self.query_service = query_service
        self.console = Console()

    def execute(self, args):
        """Execute the list command to display all bookings."""
        self.console.print(Panel.fit("[bold blue]Meeting Room Bookings[/bold blue]", border_style="blue"))

        try:
            # Parse command line arguments for sorting
            sort_by = self._parse_sort_option(args)

            # Get all bookings
            bookings = self.query_service.get_all_bookings()

            if not bookings:
                self._display_empty_state()
                return

            # Sort bookings if requested
            sorted_bookings = self._sort_bookings(bookings, sort_by)

            # Display bookings in a table
            self._display_bookings_table(sorted_bookings)

            # Display summary information
            self._display_summary(sorted_bookings)

        except Exception as e:
            self.console.print(
                Panel.fit(
                    f"[bold red]Error retrieving bookings![/bold red]\nAn error occurred: {e!s}", border_style="red"
                )
            )

    def _parse_sort_option(self, args):
        """Parse command line arguments to determine sorting option."""
        if len(args) >= 2 and args[0] == "--sort":
            sort_option = args[1].lower()
            if sort_option in ["time", "booker", "attendees"]:
                return sort_option
            else:
                self.console.print(
                    f"[yellow]Warning: Invalid sort option '{sort_option}'. Using default sorting.[/yellow]"
                )
        return "time"  # Default sort by time

    def _sort_bookings(self, bookings, sort_by):
        """Sort bookings based on the specified criteria."""
        try:
            if sort_by == "time":
                return sorted(bookings, key=lambda x: self._parse_datetime_safe(x["start_time"]))
            elif sort_by == "booker":
                return sorted(bookings, key=lambda x: x["booker"].lower())
            elif sort_by == "attendees":
                return sorted(bookings, key=lambda x: x["attendees"], reverse=True)
            else:
                return bookings
        except (KeyError, TypeError) as e:
            self.console.print(f"[yellow]Warning: Error sorting bookings: {e}. Using original order.[/yellow]")
            return bookings

    def _parse_datetime_safe(self, datetime_str):
        """Safely parse datetime string, returning a default value if parsing fails."""
        try:
            return datetime.fromisoformat(datetime_str)
        except (ValueError, TypeError):
            # Return a very old date for invalid datetime strings so they appear first
            return datetime.min

    def _display_empty_state(self):
        """Display message when no bookings exist."""
        self.console.print(
            Panel.fit(
                "[bold yellow]No bookings found![/bold yellow]\nThe meeting room is currently available for booking.",
                border_style="yellow",
            )
        )

    def _display_bookings_table(self, bookings):
        """Display bookings in a formatted table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Booking ID", style="cyan", width=12)
        table.add_column("Start Time", style="green", width=16)
        table.add_column("End Time", style="green", width=16)
        table.add_column("Booker", style="white", width=15)
        table.add_column("Attendees", style="yellow", justify="center", width=9)
        table.add_column("Duration", style="blue", width=10)

        for booking in bookings:
            try:
                # Parse datetime strings
                start_time = datetime.fromisoformat(booking["start_time"])
                end_time = datetime.fromisoformat(booking["end_time"])

                # Calculate duration
                duration = end_time - start_time
                duration_str = self._format_duration(duration)

                # Format times for display
                start_str = start_time.strftime("%Y-%m-%d %H:%M")
                end_str = end_time.strftime("%Y-%m-%d %H:%M")

                table.add_row(
                    booking["booking_id"],
                    start_str,
                    end_str,
                    booking["booker"],
                    str(booking["attendees"]),
                    duration_str,
                )

            except (ValueError, KeyError, TypeError) as e:
                # Handle malformed booking data gracefully
                table.add_row(
                    booking.get("booking_id", "N/A"),
                    booking.get("start_time", "Invalid"),
                    booking.get("end_time", "Invalid"),
                    booking.get("booker", "N/A"),
                    str(booking.get("attendees", "N/A")),
                    "N/A",
                )
                self.console.print(f"[yellow]Warning: Malformed booking data: {e}[/yellow]")

        self.console.print(table)

    def _format_duration(self, duration):
        """Format duration timedelta as a human-readable string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def _display_summary(self, bookings):
        """Display summary information about the bookings."""
        total_bookings = len(bookings)
        total_attendees = sum(booking.get("attendees", 0) for booking in bookings)

        # Calculate total duration
        total_duration_seconds = 0
        for booking in bookings:
            try:
                start_time = datetime.fromisoformat(booking["start_time"])
                end_time = datetime.fromisoformat(booking["end_time"])
                duration = end_time - start_time
                total_duration_seconds += duration.total_seconds()
            except (ValueError, KeyError, TypeError):
                continue

        total_hours = int(total_duration_seconds // 3600)
        total_minutes = int((total_duration_seconds % 3600) // 60)

        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column("Metric", style="bold cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Total Bookings:", str(total_bookings))
        summary_table.add_row("Total Attendees:", str(total_attendees))
        summary_table.add_row("Total Duration:", f"{total_hours}h {total_minutes}m")

        if total_bookings > 0:
            avg_attendees = total_attendees / total_bookings
            summary_table.add_row("Avg Attendees:", f"{avg_attendees:.1f}")

        self.console.print("\n[bold]Summary:[/bold]")
        self.console.print(summary_table)
