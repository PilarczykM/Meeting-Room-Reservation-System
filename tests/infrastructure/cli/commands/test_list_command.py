from unittest.mock import Mock

import pytest

from src.application.services.query_service import QueryService
from src.infrastructure.cli.commands.list_command import ListCommand


class TestListCommand:
    """Test suite for the ListCommand CLI command."""

    @pytest.fixture
    def mock_query_service(self):
        """Create a mock query service for testing."""
        return Mock(spec=QueryService)

    @pytest.fixture
    def mock_console(self):
        """Create a mock console for testing output."""
        return Mock()

    @pytest.fixture
    def list_command(self, mock_query_service, mock_console):
        """Create a ListCommand instance with mocked dependencies."""
        command = ListCommand(mock_query_service)
        command.console = mock_console  # Inject the mock console
        return command

    def test_list_command_initialization(self, mock_query_service):
        """Test that ListCommand initializes correctly."""
        command = ListCommand(mock_query_service)
        assert command.query_service == mock_query_service
        assert hasattr(command, "console")

    def test_list_bookings_with_data(self, list_command, mock_console, mock_query_service):
        """Test listing bookings when bookings exist."""
        # Arrange
        mock_bookings = [
            {
                "booking_id": "booking-123",
                "start_time": "2025-07-16T10:00:00",
                "end_time": "2025-07-16T11:00:00",
                "booker": "John Doe",
                "attendees": 8,
            },
            {
                "booking_id": "booking-456",
                "start_time": "2025-07-16T14:00:00",
                "end_time": "2025-07-16T15:30:00",
                "booker": "Jane Smith",
                "attendees": 12,
            },
        ]

        mock_query_service.get_all_bookings.return_value = mock_bookings

        # Act
        list_command.execute([])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_bookings_empty_state(self, list_command, mock_console, mock_query_service):
        """Test listing bookings when no bookings exist."""
        # Arrange
        mock_query_service.get_all_bookings.return_value = []

        # Act
        list_command.execute([])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_bookings_service_error(self, list_command, mock_console, mock_query_service):
        """Test handling of query service errors."""
        # Arrange
        mock_query_service.get_all_bookings.side_effect = Exception("Database error")

        # Act
        list_command.execute([])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_bookings_with_sorting_by_time(self, list_command, mock_console, mock_query_service):
        """Test listing bookings with time-based sorting."""
        # Arrange
        mock_bookings = [
            {
                "booking_id": "booking-456",
                "start_time": "2025-07-16T14:00:00",
                "end_time": "2025-07-16T15:30:00",
                "booker": "Jane Smith",
                "attendees": 12,
            },
            {
                "booking_id": "booking-123",
                "start_time": "2025-07-16T10:00:00",
                "end_time": "2025-07-16T11:00:00",
                "booker": "John Doe",
                "attendees": 8,
            },
        ]

        mock_query_service.get_all_bookings.return_value = mock_bookings

        # Act
        list_command.execute(["--sort", "time"])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_bookings_with_sorting_by_booker(self, list_command, mock_console, mock_query_service):
        """Test listing bookings with booker-based sorting."""
        # Arrange
        mock_bookings = [
            {
                "booking_id": "booking-123",
                "start_time": "2025-07-16T10:00:00",
                "end_time": "2025-07-16T11:00:00",
                "booker": "John Doe",
                "attendees": 8,
            },
            {
                "booking_id": "booking-456",
                "start_time": "2025-07-16T14:00:00",
                "end_time": "2025-07-16T15:30:00",
                "booker": "Jane Smith",
                "attendees": 12,
            },
        ]

        mock_query_service.get_all_bookings.return_value = mock_bookings

        # Act
        list_command.execute(["--sort", "booker"])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_bookings_with_invalid_sort_option(self, list_command, mock_console, mock_query_service):
        """Test handling of invalid sort options."""
        # Arrange
        mock_bookings = [
            {
                "booking_id": "booking-123",
                "start_time": "2025-07-16T10:00:00",
                "end_time": "2025-07-16T11:00:00",
                "booker": "John Doe",
                "attendees": 8,
            }
        ]

        mock_query_service.get_all_bookings.return_value = mock_bookings

        # Act
        list_command.execute(["--sort", "invalid"])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_bookings_with_malformed_datetime(self, list_command, mock_console, mock_query_service):
        """Test handling of malformed datetime strings in booking data."""
        # Arrange
        mock_bookings = [
            {
                "booking_id": "booking-123",
                "start_time": "invalid-datetime",
                "end_time": "2025-07-16T11:00:00",
                "booker": "John Doe",
                "attendees": 8,
            }
        ]

        mock_query_service.get_all_bookings.return_value = mock_bookings

        # Act
        list_command.execute([])

        # Assert
        mock_query_service.get_all_bookings.assert_called_once()
        mock_console.print.assert_called()

    def test_list_command_docstring(self, list_command):
        """Test that the command has appropriate documentation."""
        assert list_command.__doc__ is not None
        assert "list" in list_command.__doc__.lower()
