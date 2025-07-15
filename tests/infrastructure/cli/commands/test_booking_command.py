from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.application.dtos.booking_response import BookingResponse
from src.application.services.booking_service import BookingService
from src.domain.exceptions import OverlappingBookingError
from src.infrastructure.cli.commands.booking_command import BookingCommand


class TestBookingCommand:
    """Test suite for the BookingCommand CLI command."""

    @pytest.fixture
    def mock_booking_service(self):
        """Create a mock booking service for testing."""
        return Mock(spec=BookingService)

    @pytest.fixture
    def booking_command(self, mock_booking_service, mock_console):
        """Create a BookingCommand instance with mocked dependencies."""
        command = BookingCommand(mock_booking_service)
        command.console = mock_console  # Inject the mock console
        return command

    @pytest.fixture
    def mock_console(self):
        """Create a mock console for testing output."""
        return Mock()

    def test_booking_command_initialization(self, mock_booking_service):
        """Test that BookingCommand initializes correctly."""
        command = BookingCommand(mock_booking_service)
        assert command.booking_service == mock_booking_service
        assert hasattr(command, "console")

    @patch("builtins.input")
    def test_successful_booking_flow(self, mock_input, booking_command, mock_console, mock_booking_service):
        """Test successful booking creation through CLI interaction."""
        # Arrange
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)

        mock_input.side_effect = [
            start_time.strftime("%Y-%m-%d %H:%M"),  # start time
            end_time.strftime("%Y-%m-%d %H:%M"),  # end time
            "John Doe",  # booker name
            "8",  # attendees
            "y",  # confirmation
        ]

        mock_response = BookingResponse(
            booking_id="booking-123", start_time=start_time, end_time=end_time, booker="John Doe", attendees=8
        )
        mock_booking_service.create_booking.return_value = mock_response

        # Act
        booking_command.execute([])

        # Assert
        mock_booking_service.create_booking.assert_called_once()
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_booking_with_invalid_date_format(self, mock_input, booking_command, mock_console):
        """Test handling of invalid date format input."""
        # Arrange
        mock_input.side_effect = [
            "invalid-date",  # invalid start time
            "2024-12-25 10:00",  # valid start time (retry)
            "2024-12-25 11:00",  # valid end time
            "John Doe",  # booker name
            "8",  # attendees
            "n",  # cancel confirmation
        ]

        # Act
        booking_command.execute([])

        # Assert
        # Should show error message for invalid date format
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_booking_with_invalid_attendees_count(self, mock_input, booking_command, mock_console):
        """Test handling of invalid attendees count."""
        # Arrange
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)

        mock_input.side_effect = [
            start_time.strftime("%Y-%m-%d %H:%M"),  # start time
            end_time.strftime("%Y-%m-%d %H:%M"),  # end time
            "John Doe",  # booker name
            "2",  # invalid attendees (too few)
            "8",  # valid attendees (retry)
            "n",  # cancel confirmation
        ]

        # Act
        booking_command.execute([])

        # Assert
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_booking_conflict_error_handling(self, mock_input, booking_command, mock_console, mock_booking_service):
        """Test handling of booking conflict errors."""
        # Arrange
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)

        mock_input.side_effect = [
            start_time.strftime("%Y-%m-%d %H:%M"),  # start time
            end_time.strftime("%Y-%m-%d %H:%M"),  # end time
            "John Doe",  # booker name
            "8",  # attendees
            "y",  # confirmation
        ]

        mock_booking_service.create_booking.side_effect = OverlappingBookingError("Time slot already booked")

        # Act
        booking_command.execute([])

        # Assert
        mock_booking_service.create_booking.assert_called_once()
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_user_cancels_booking_confirmation(self, mock_input, booking_command, mock_console, mock_booking_service):
        """Test user canceling the booking at confirmation step."""
        # Arrange
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)

        mock_input.side_effect = [
            start_time.strftime("%Y-%m-%d %H:%M"),  # start time
            end_time.strftime("%Y-%m-%d %H:%M"),  # end time
            "John Doe",  # booker name
            "8",  # attendees
            "n",  # cancel confirmation
        ]

        # Act
        booking_command.execute([])

        # Assert
        mock_booking_service.create_booking.assert_not_called()
        mock_console.print.assert_called()

    def test_booking_command_docstring(self, booking_command):
        """Test that the command has appropriate documentation."""
        assert booking_command.__doc__ is not None
        assert "book" in booking_command.__doc__.lower()
