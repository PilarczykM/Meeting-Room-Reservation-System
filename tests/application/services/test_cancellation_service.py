from unittest.mock import MagicMock

import pytest

from src.application.commands.commands import CancelBookingCommand
from src.application.dtos.cancellation_request import CancellationRequest
from src.application.exceptions import CancellationFailedError
from src.application.services.cancellation_service import CancellationService
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
    request = CancellationRequest(booking_id=booking_id)
    command = CancelBookingCommand(request=request)

    cancellation_service.booking_repository.get_by_id.return_value = mock_booking

    # Act
    cancellation_service.cancel_booking(command)

    # Assert
    cancellation_service.booking_repository.delete.assert_called_once_with(booking_id)


def test_cancel_booking_not_found_error(cancellation_service):
    # Arrange
    booking_id = "non-existent-booking-id"
    request = CancellationRequest(booking_id=booking_id)
    command = CancelBookingCommand(request=request)

    cancellation_service.booking_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(CancellationFailedError):
        cancellation_service.cancel_booking(command)
