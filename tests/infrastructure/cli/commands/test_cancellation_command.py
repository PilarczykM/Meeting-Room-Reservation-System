from unittest.mock import Mock, patch

import pytest

from src.application.exceptions import CancellationFailedError
from src.application.services.cancellation_service import CancellationService
from src.application.services.query_service import QueryService
from src.infrastructure.cli.commands.cancellation_command import CancellationCommand


class TestCancellationCommand:
    """Test suite for the CancellationCommand CLI command."""

    @pytest.fixture
    def mock_cancellation_service(self):
        """Create a mock cancellation service for testing."""
        return Mock(spec=CancellationService)

    @pytest.fixture
    def mock_query_service(self):
        """Create a mock query service for testing."""
        return Mock(spec=QueryService)

    @pytest.fixture
    def mock_console(self):
        """Create a mock console for testing output."""
        return Mock()

    @pytest.fixture
    def cancellation_command(self, mock_cancellation_service, mock_query_service, mock_console):
        """Create a CancellationCommand instance with mocked dependencies."""
        command = CancellationCommand(mock_cancellation_service, mock_query_service)
        command.console = mock_console  # Inject the mock console
        return command

    def test_cancellation_command_initialization(self, mock_cancellation_service, mock_query_service):
        """Test that CancellationCommand initializes correctly."""
        command = CancellationCommand(mock_cancellation_service, mock_query_service)
        assert command.cancellation_service == mock_cancellation_service
        assert command.query_service == mock_query_service
        assert hasattr(command, "console")

    @patch("builtins.input")
    def test_successful_cancellation_flow(
        self, mock_input, cancellation_command, mock_console, mock_cancellation_service, mock_query_service
    ):
        """Test successful booking cancellation through CLI interaction."""
        # Arrange
        booking_id = "booking-123"
        mock_booking = {
            "booking_id": booking_id,
            "start_time": "2025-07-16T10:00:00",
            "end_time": "2025-07-16T11:00:00",
            "booker": "John Doe",
            "attendees": 8,
        }

        mock_input.side_effect = [
            booking_id,  # booking ID input
            "y",  # confirmation
        ]

        mock_query_service.get_all_bookings.return_value = [mock_booking]

        # Act
        cancellation_command.execute([])

        # Assert
        mock_cancellation_service.cancel_booking.assert_called_once()
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_cancellation_with_invalid_booking_id(
        self, mock_input, cancellation_command, mock_console, mock_query_service
    ):
        """Test handling of invalid booking ID."""
        # Arrange
        mock_input.side_effect = [
            "invalid-id",  # invalid booking ID
            "",  # empty input to exit
        ]

        mock_query_service.get_all_bookings.return_value = []

        # Act
        cancellation_command.execute([])

        # Assert
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_cancellation_service_error_handling(
        self, mock_input, cancellation_command, mock_console, mock_cancellation_service, mock_query_service
    ):
        """Test handling of cancellation service errors."""
        # Arrange
        booking_id = "booking-123"
        mock_booking = {
            "booking_id": booking_id,
            "start_time": "2025-07-16T10:00:00",
            "end_time": "2025-07-16T11:00:00",
            "booker": "John Doe",
            "attendees": 8,
        }

        mock_input.side_effect = [
            booking_id,  # booking ID input
            "y",  # confirmation
        ]

        mock_query_service.get_all_bookings.return_value = [mock_booking]
        mock_cancellation_service.cancel_booking.side_effect = CancellationFailedError("Booking not found")

        # Act
        cancellation_command.execute([])

        # Assert
        mock_cancellation_service.cancel_booking.assert_called_once()
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_user_cancels_confirmation(
        self, mock_input, cancellation_command, mock_console, mock_cancellation_service, mock_query_service
    ):
        """Test user canceling the confirmation step."""
        # Arrange
        booking_id = "booking-123"
        mock_booking = {
            "booking_id": booking_id,
            "start_time": "2025-07-16T10:00:00",
            "end_time": "2025-07-16T11:00:00",
            "booker": "John Doe",
            "attendees": 8,
        }

        mock_input.side_effect = [
            booking_id,  # booking ID input
            "n",  # cancel confirmation
        ]

        mock_query_service.get_all_bookings.return_value = [mock_booking]

        # Act
        cancellation_command.execute([])

        # Assert
        mock_cancellation_service.cancel_booking.assert_not_called()
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_empty_booking_id_input(self, mock_input, cancellation_command, mock_console):
        """Test handling of empty booking ID input."""
        # Arrange
        mock_input.side_effect = [""]  # empty input

        # Act
        cancellation_command.execute([])

        # Assert
        mock_console.print.assert_called()

    @patch("builtins.input")
    def test_booking_lookup_and_display(self, mock_input, cancellation_command, mock_console, mock_query_service):
        """Test that booking details are displayed for confirmation."""
        # Arrange
        booking_id = "booking-123"
        mock_booking = {
            "booking_id": booking_id,
            "start_time": "2025-07-16T10:00:00",
            "end_time": "2025-07-16T11:00:00",
            "booker": "John Doe",
            "attendees": 8,
        }

        mock_input.side_effect = [
            booking_id,  # booking ID input
            "n",  # cancel confirmation
        ]

        mock_query_service.get_all_bookings.return_value = [mock_booking]

        # Act
        cancellation_command.execute([])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_cancellation_command_docstring(self, cancellation_command):
        """Test that the command has appropriate documentation."""
        assert cancellation_command.__doc__ is not None
        assert "cancel" in cancellation_command.__doc__.lower()
