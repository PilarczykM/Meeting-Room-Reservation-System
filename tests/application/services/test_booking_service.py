import logging
from unittest.mock import MagicMock

import pytest

from src.application.services.booking_service import BookingService
from src.domain.entities.booking import Booking
from src.domain.entities.timeslot import TimeSlot
from src.domain.exceptions import InvalidAttendeeCountError, OverlappingBookingError


@pytest.fixture
def booking_service():
    booking_repository = MagicMock()
    return BookingService(booking_repository)


def test_create_booking_success(booking_service):
    # Arrange
    start_time = "2025-07-15T10:00:00"
    end_time = "2025-07-15T11:00:00"
    booker_id = "user123"
    attendees = 10

    # Act
    booking_service.create_booking(start_time, end_time, booker_id, attendees)

    # Assert
    booking_service.booking_repository.add.assert_called_once()


def test_create_booking_overlapping_error(booking_service):
    # Arrange
    start_time = "2025-07-15T10:00:00"
    end_time = "2025-07-15T11:00:00"
    booker_id = "user123"
    attendees = 10

    existing_timeslot = TimeSlot.create(start_time, end_time)
    existing_booking = Booking.create(existing_timeslot, booker_id, attendees)

    # Mock the repository to return an existing booking
    booking_service.booking_repository.get_all.return_value = [existing_booking]

    # Act & Assert
    with pytest.raises(OverlappingBookingError):
        booking_service.create_booking(start_time, end_time, booker_id, attendees)


def test_create_booking_invalid_attendees_error(booking_service):
    # Arrange
    start_time = "2025-07-15T10:00:00"
    end_time = "2025-07-15T11:00:00"
    booker_id = "user123"
    attendees = 2  # Invalid number of attendees

    # Act & Assert
    with pytest.raises(InvalidAttendeeCountError):
        booking_service.create_booking(start_time, end_time, booker_id, attendees)


def test_create_booking_logging(booking_service, caplog):
    # Arrange
    start_time = "2025-07-15T10:00:00"
    end_time = "2025-07-15T11:00:00"
    booker_id = "user123"
    attendees = 10

    with caplog.at_level(logging.INFO):
        booking_service.create_booking(start_time, end_time, booker_id, attendees)
        assert f"Attempting to create booking for {booker_id}" in caplog.messages[0]
        assert "Booking created successfully" in caplog.messages[1]
