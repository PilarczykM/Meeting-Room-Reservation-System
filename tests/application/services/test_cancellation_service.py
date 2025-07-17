from unittest.mock import MagicMock

import pytest

from src.application.commands.commands import CancelBookingCommand
from src.application.dtos.cancellation_request import CancellationRequest
from src.application.exceptions import CancellationFailedError
from src.application.services.cancellation_service import CancellationService
from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot


@pytest.fixture
def cancellation_service():
    booking_repository = MagicMock()
    return CancellationService(booking_repository)


def test_cancel_booking_success(cancellation_service):
    # Arrange
    booking_id = "test-booking-id"
    mock_booking = Booking.create(
        TimeSlot.create("2025-07-15T10:00:00", "2025-07-15T11:00:00"), "booker", 10, booking_id=booking_id
    )

    # Create a meeting room with the booking
    meeting_room = MeetingRoom(room_id="main-room")
    meeting_room.bookings = [mock_booking]

    request = CancellationRequest(booking_id=booking_id)
    command = CancelBookingCommand(request=request)

    # Mock the repository to return the meeting room
    cancellation_service.booking_repository.find_by_id.return_value = meeting_room

    # Act
    cancellation_service.cancel_booking(command)

    # Assert
    cancellation_service.booking_repository.save.assert_called_once_with(meeting_room)
    assert len(meeting_room.bookings) == 0  # Booking should be removed


def test_cancel_booking_not_found_error(cancellation_service):
    # Arrange
    booking_id = "non-existent-booking-id"
    request = CancellationRequest(booking_id=booking_id)
    command = CancelBookingCommand(request=request)

    # Mock the repository to return None (no meeting room found)
    cancellation_service.booking_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(CancellationFailedError):
        cancellation_service.cancel_booking(command)
